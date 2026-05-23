interface Env {
	GROQ_API_KEY: string;
}

type ChatRole = "user" | "assistant";

interface ChatMessage {
	role: ChatRole;
	content: string;
}

const GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions";
const GROQ_MODEL = "llama-3.3-70b-versatile";
const MAX_MESSAGE_LENGTH = 4000;
const MAX_HISTORY_ITEMS = 6;

const ALLOWED_ORIGINS = new Set([
	"https://oceancloudconsults.com",
	"https://www.oceancloudconsults.com",
	"http://localhost:8787",
	"http://127.0.0.1:8787",
]);

const SYSTEM_PROMPT = `You are OceanBot, the AI assistant for OceanCloud — a Microsoft Solutions Partner based in the United States specialising in SharePoint Online, Microsoft 365, Power Platform, Microsoft Teams, Viva, and workplace transformation.

ABOUT OCEANCLOUD:
- Microsoft Solutions Partner with Modern Work and Security designations
- Founded 2013 | 15 certified consultants | 150+ projects delivered | 98% client satisfaction
- 40+ active Microsoft certifications: MS-102, MS-203, SC-300, SC-400, PL-400, PL-600, AZ-104
- Fixed-price engagements, no time-and-materials billing surprises
- Every project includes 12 months post-go-live hypercare support
- Free 60-minute discovery call available — no obligation

SERVICES & PRICING (fixed-price):
- SharePoint intranet build: from $7,500 (small, <200 users) | $20,000 (mid, 200-500) | $55,000+ (enterprise 500+)
- M365 migration: from $18-$30/user (minimum project fee $3,500)
- Power Apps: from $4,500 | Power Automate workflows: from $2,500 | Power BI dashboards: from $3,000
- Security & Compliance (Zero Trust/Entra ID/Purview/Defender): from $4,000
- Advisory retainer: from $2,200/month
- Teams & Viva implementation: scoped per project

TYPICAL TIMELINES:
- SharePoint intranet: 8-12 weeks
- M365 migration (100-500 users): 4-8 weeks | Enterprise (500+): 10-16 weeks
- Power Platform app: 3-6 weeks
- Security uplift: 4-8 weeks

CONTACT:
- Phone: +1 (469) 809-4053
- WhatsApp: +1 (917) 675-3126
- Email: oceancloudconsults@gmail.com
- Hours: Monday-Friday, 9am-6pm EST
- Book a call: contact

RESPONSE RULES:
- Answer questions about SharePoint, Microsoft 365, Power Platform, Teams, security, and OceanCloud's services
- For general Microsoft 365 / SharePoint technical questions, give accurate, genuinely helpful answers
- Keep responses concise — 3-5 sentences or a short bullet list (max 5 bullets)
- Use plain text only — no markdown asterisks or hashes; use simple line breaks
- Always naturally mention the free discovery call when someone asks about scoping, timelines, or costs
- If asked something completely unrelated to Microsoft/SharePoint/OceanCloud, politely say you specialise in M365 topics and offer to connect them with the team
- Never make up pricing, certifications, or case study details not listed above`;

function isAllowedOrigin(origin: string | null): origin is string {
	return Boolean(origin && ALLOWED_ORIGINS.has(origin));
}

function corsHeaders(origin: string): HeadersInit {
	return {
		"Access-Control-Allow-Origin": origin,
		"Access-Control-Allow-Headers": "Content-Type",
		"Access-Control-Allow-Methods": "POST, OPTIONS",
		"Access-Control-Max-Age": "86400",
		"Vary": "Origin",
	};
}

function jsonResponse(data: unknown, status: number, origin: string): Response {
	return new Response(JSON.stringify(data), {
		status,
		headers: {
			"Content-Type": "application/json; charset=utf-8",
			"Cache-Control": "no-store",
			...corsHeaders(origin),
		},
	});
}

function sanitizeHistory(value: unknown): ChatMessage[] {
	if (!Array.isArray(value)) return [];

	return value
		.filter((item): item is ChatMessage => {
			return (
				item !== null &&
				typeof item === "object" &&
				["user", "assistant"].includes((item as ChatMessage).role) &&
				typeof (item as ChatMessage).content === "string"
			);
		})
		.slice(-MAX_HISTORY_ITEMS)
		.map((item) => ({
			role: item.role,
			content: item.content.slice(0, MAX_MESSAGE_LENGTH),
		}));
}

async function handleChat(request: Request, env: Env, origin: string): Promise<Response> {
	if (!env.GROQ_API_KEY) {
		return jsonResponse({ error: "AI service is not configured" }, 500, origin);
	}

	let payload: Record<string, unknown>;
	try {
		payload = (await request.json()) as Record<string, unknown>;
	} catch {
		return jsonResponse({ error: "Invalid JSON body" }, 400, origin);
	}

	const message = String(payload.message || "").trim().slice(0, MAX_MESSAGE_LENGTH);
	if (!message) {
		return jsonResponse({ error: "Missing message" }, 400, origin);
	}

	const groqResponse = await fetch(GROQ_ENDPOINT, {
		method: "POST",
		headers: {
			"Authorization": `Bearer ${env.GROQ_API_KEY}`,
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			model: GROQ_MODEL,
			messages: [
				{ role: "system", content: SYSTEM_PROMPT },
				...sanitizeHistory(payload.history),
				{ role: "user", content: message },
			],
			max_tokens: 420,
			temperature: 0.6,
			top_p: 0.9,
		}),
	});

	const groqData = await groqResponse.json().catch(() => null) as any;
	if (!groqResponse.ok) {
		return jsonResponse(
			{ error: groqData?.error?.message || `AI service returned HTTP ${groqResponse.status}` },
			502,
			origin,
		);
	}

	const reply = String(groqData?.choices?.[0]?.message?.content || "").trim();
	if (!reply) {
		return jsonResponse({ error: "AI service returned an empty response" }, 502, origin);
	}

	return jsonResponse({ reply }, 200, origin);
}

export default {
	async fetch(request, env): Promise<Response> {
		const origin = request.headers.get("Origin");
		if (!isAllowedOrigin(origin)) {
			return new Response("Forbidden", { status: 403 });
		}

		if (request.method === "OPTIONS") {
			return new Response(null, { status: 204, headers: corsHeaders(origin) });
		}

		const url = new URL(request.url);
		if (request.method === "GET" && url.pathname === "/") {
			return jsonResponse({ ok: true, service: "OceanCloud AI proxy" }, 200, origin);
		}

		if (request.method !== "POST" || !["/", "/chat"].includes(url.pathname)) {
			return jsonResponse({ error: "Not found" }, 404, origin);
		}

		return handleChat(request, env, origin);
	},
} satisfies ExportedHandler<Env>;
