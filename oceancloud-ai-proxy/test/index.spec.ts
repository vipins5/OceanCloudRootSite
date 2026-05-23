import { describe, expect, it, vi } from "vitest";
import worker from "../src/index";

const IncomingRequest = Request<unknown, IncomingRequestCfProperties>;
const env = { GROQ_API_KEY: "test-key" };
const allowedOrigin = "https://oceancloudconsults.com";

function request(path: string, init: RequestInit = {}) {
	const headers = new Headers(init.headers);
	headers.set("Origin", headers.get("Origin") || allowedOrigin);

	return new IncomingRequest(`https://example.com${path}`, {
		...init,
		headers,
	} as any);
}

describe("OceanCloud AI proxy", () => {
	it("rejects requests from unknown origins", async () => {
		const response = await worker.fetch(
			new IncomingRequest("https://example.com/chat", {
				method: "POST",
				headers: { Origin: "https://example.net" },
			} as any),
			env,
		);

		expect(response.status).toBe(403);
	});

	it("returns CORS headers for preflight requests", async () => {
		const response = await worker.fetch(request("/chat", { method: "OPTIONS" }), env);

		expect(response.status).toBe(204);
		expect(response.headers.get("Access-Control-Allow-Origin")).toBe(allowedOrigin);
	});

	it("requires a message", async () => {
		const response = await worker.fetch(
			request("/chat", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ message: "" }),
			}),
			env,
		);

		expect(response.status).toBe(400);
		expect(await response.json()).toEqual({ error: "Missing message" });
	});

	it("proxies successful Groq responses", async () => {
		vi.stubGlobal(
			"fetch",
			vi.fn().mockResolvedValue(
				new Response(
					JSON.stringify({ choices: [{ message: { content: "SharePoint governance keeps sites organized." } }] }),
					{ status: 200, headers: { "Content-Type": "application/json" } },
				),
			),
		);

		const response = await worker.fetch(
			request("/chat", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ message: "What is SharePoint governance?" }),
			}),
			env,
		);

		expect(response.status).toBe(200);
		expect(await response.json()).toEqual({ reply: "SharePoint governance keeps sites organized." });
		expect(fetch).toHaveBeenCalledOnce();

		vi.unstubAllGlobals();
	});
});
