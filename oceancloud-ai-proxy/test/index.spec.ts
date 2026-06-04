import { describe, expect, it, vi } from "vitest";
import worker from "../src/index";

const IncomingRequest = Request<unknown, IncomingRequestCfProperties>;
const env = { GROQ_API_KEY: "test-key" };
const healthEnv = {
	...env,
	M365_HEALTH_TENANT_ID: "tenant-id",
	M365_HEALTH_CLIENT_ID: "client-id",
	M365_HEALTH_CLIENT_SECRET: "client-secret",
};
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

	it("reports when Microsoft 365 service health is not configured", async () => {
		const response = await worker.fetch(request("/m365/service-health?region=emea"), env);
		const data = await response.json() as any;

		expect(response.status).toBe(503);
		expect(data.configured).toBe(false);
		expect(data.region).toBe("emea");
		expect(data.requiredSecrets).toContain("M365_HEALTH_TENANT_ID");
	});

	it("returns Microsoft 365 service health summaries with region filtering", async () => {
		vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
			const url = String(input);
			if (url.includes("/oauth2/v2.0/token")) {
				return new Response(JSON.stringify({ access_token: "graph-token" }), {
					status: 200,
					headers: { "Content-Type": "application/json" },
				});
			}
			if (url.includes("/admin/serviceAnnouncement/healthOverviews")) {
				return new Response(JSON.stringify({
					value: [
						{ id: "Exchange", service: "Exchange Online", status: "ServiceDegradation" },
						{ id: "Teams", service: "Microsoft Teams", status: "ServiceOperational" },
					],
				}), { status: 200, headers: { "Content-Type": "application/json" } });
			}
			if (url.includes("/admin/serviceAnnouncement/issues")) {
				return new Response(JSON.stringify({
					value: [
						{
							id: "EX1",
							title: "Users in Europe may be unable to access Exchange Online",
							classification: "Incident",
							status: "ServiceDegradation",
							service: "Exchange Online",
							isResolved: false,
							lastModifiedDateTime: "2026-06-04T12:00:00Z",
							startDateTime: "2026-06-04T10:00:00Z",
							feature: "Calendar",
							featureGroup: "Exchange Online",
							impactDescription: "Impact is scoped to EMEA users.",
							details: [{ name: "Current status", value: "Microsoft is investigating the source of the impact." }],
							posts: [{ createdDateTime: "2026-06-04T12:15:00Z", description: { content: "<p>Admins can review EX1 in the Microsoft 365 admin center.</p>" } }],
						},
						{
							id: "TM1",
							title: "Some users in the United States may see Teams latency",
							classification: "Advisory",
							status: "Investigating",
							service: "Microsoft Teams",
							isResolved: false,
							lastModifiedDateTime: "2026-06-04T11:00:00Z",
						},
					],
				}), { status: 200, headers: { "Content-Type": "application/json" } });
			}
			return new Response("not found", { status: 404 });
		}));

		const response = await worker.fetch(request("/m365/service-health?region=emea"), healthEnv);
		const data = await response.json() as any;

		expect(response.status).toBe(200);
		expect(data.configured).toBe(true);
		expect(data.region).toBe("emea");
		expect(data.regionMode).toBe("text-match");
		expect(data.totals.matchingIssues).toBe(1);
		expect(data.totals.incidents).toBe(1);
		expect(data.issues[0].id).toBe("EX1");
		expect(data.issues[0].feature).toBe("Calendar");
		expect(data.issues[0].details[0]).toEqual({ name: "Current status", value: "Microsoft is investigating the source of the impact." });
		expect(data.issues[0].posts[0]).toEqual({
			createdDateTime: "2026-06-04T12:15:00Z",
			content: "Admins can review EX1 in the Microsoft 365 admin center.",
		});

		vi.unstubAllGlobals();
	});

	it("returns structured Microsoft Graph service health failures", async () => {
		vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
			const url = String(input);
			if (url.includes("/oauth2/v2.0/token")) {
				return new Response(JSON.stringify({ access_token: "graph-token" }), {
					status: 200,
					headers: { "Content-Type": "application/json" },
				});
			}
			return new Response(JSON.stringify({ error: { message: "Missing ServiceHealth.Read.All permission" } }), {
				status: 403,
				headers: { "Content-Type": "application/json" },
			});
		}));

		const response = await worker.fetch(request("/m365/service-health?region=global"), healthEnv);
		const data = await response.json() as any;

		expect(response.status).toBe(502);
		expect(data.configured).toBe(true);
		expect(data.error).toBe("Microsoft Graph service health request failed");
		expect(data.detail).toContain("Missing ServiceHealth.Read.All permission");

		vi.unstubAllGlobals();
	});
});
