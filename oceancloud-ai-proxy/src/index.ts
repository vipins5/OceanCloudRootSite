interface Env {
	GROQ_API_KEY: string;
	COMMENTS_DB?: D1Database;
	MICROSOFT_CLIENT_ID?: string;
	MICROSOFT_CLIENT_SECRET?: string;
	GOOGLE_CLIENT_ID?: string;
	GOOGLE_CLIENT_SECRET?: string;
	GITHUB_CLIENT_ID?: string;
	GITHUB_CLIENT_SECRET?: string;
	COMMENT_SESSION_SECRET?: string;
	TURNSTILE_SECRET_KEY?: string;
	TURNSTILE_SITE_KEY?: string;
	ADMIN_TOKEN?: string;
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
	"http://localhost:8000",
	"http://127.0.0.1:8000",
	"http://localhost:8787",
	"http://127.0.0.1:8787",
]);

const COMMENT_SESSION_TTL_SECONDS = 60 * 60 * 24 * 30;
const COMMENT_MAX_LENGTH = 2000;
const COMMENT_MIN_LENGTH = 3;
const COMMENT_MAX_THREAD_DEPTH = 1;
const MICROSOFT_AUTHORITY = "https://login.microsoftonline.com/common/oauth2/v2.0";
const GRAPH_ME_ENDPOINT = "https://graph.microsoft.com/v1.0/me?$select=id,displayName,mail,userPrincipalName";
const GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth";
const GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token";
const GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo";
const GITHUB_AUTH_ENDPOINT = "https://github.com/login/oauth/authorize";
const GITHUB_TOKEN_ENDPOINT = "https://github.com/login/oauth/access_token";
const GITHUB_USER_ENDPOINT = "https://api.github.com/user";
const GITHUB_EMAILS_ENDPOINT = "https://api.github.com/user/emails";

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
		"Access-Control-Allow-Headers": "Authorization, Content-Type",
		"Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
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

function htmlResponse(markup: string, status = 200): Response {
	return new Response(markup, {
		status,
		headers: {
			"Content-Type": "text/html; charset=utf-8",
			"Cache-Control": "no-store",
		},
	});
}

function redirectResponse(location: string, init?: ResponseInit): Response {
	return new Response(null, {
		status: 302,
		...init,
		headers: {
			Location: location,
			"Cache-Control": "no-store",
			...(init?.headers || {}),
		},
	});
}

function badConfig(origin: string): Response {
	return jsonResponse({ error: "Comments are not configured" }, 503, origin);
}

function isAllowedReturnUrl(value: string | null): value is string {
	if (!value) return false;
	try {
		const url = new URL(value);
		return ALLOWED_ORIGINS.has(url.origin);
	} catch {
		return false;
	}
}

function safeSlug(value: unknown): string {
	return String(value || "")
		.trim()
		.toLowerCase()
		.replace(/\.html$/, "")
		.replace(/[^a-z0-9-]/g, "")
		.slice(0, 120);
}

function safeDisplayName(value: unknown): string {
	return String(value || "")
		.trim()
		.replace(/\s+/g, " ")
		.slice(0, 80);
}

function safeComment(value: unknown): string {
	return String(value || "")
		.trim()
		.replace(/\r\n/g, "\n")
		.slice(0, COMMENT_MAX_LENGTH);
}

function getBearerToken(request: Request): string {
	const header = request.headers.get("Authorization") || "";
	const match = header.match(/^Bearer\s+(.+)$/i);
	return match ? match[1].trim() : "";
}

function getAdminToken(request: Request): string {
	return getBearerToken(request) || request.headers.get("x-admin-token") || "";
}

function randomToken(bytes = 32): string {
	const array = new Uint8Array(bytes);
	crypto.getRandomValues(array);
	return [...array].map((value) => value.toString(16).padStart(2, "0")).join("");
}

async function sha256Hex(value: string): Promise<string> {
	const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
	return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

async function validateTurnstile(token: string, request: Request, env: Env): Promise<boolean> {
	if (!env.TURNSTILE_SECRET_KEY) return false;
	if (!token || token.length > 2048) return false;

	const response = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			secret: env.TURNSTILE_SECRET_KEY,
			response: token,
			remoteip: request.headers.get("CF-Connecting-IP") || undefined,
		}),
	});
	const result = await response.json().catch(() => null) as { success?: boolean } | null;
	return Boolean(result?.success);
}

async function getSessionUser(request: Request, env: Env): Promise<any | null> {
	if (!env.COMMENTS_DB || !env.COMMENT_SESSION_SECRET) return null;
	const token = getBearerToken(request);
	if (!token) return null;
	const tokenHash = await sha256Hex(`${env.COMMENT_SESSION_SECRET}:${token}`);
	const row = await env.COMMENTS_DB.prepare(
		`SELECT users.id, users.provider, users.provider_user_id, users.display_name, users.email, users.email_hash
		 FROM comment_sessions
		 JOIN comment_users users ON users.id = comment_sessions.user_id
		 WHERE comment_sessions.token_hash = ? AND comment_sessions.expires_at > datetime('now')`,
	).bind(tokenHash).first();
	return row || null;
}

async function handleCommentsConfig(env: Env, origin: string): Promise<Response> {
	return jsonResponse({
		turnstileSiteKey: env.TURNSTILE_SITE_KEY || "",
		providers: {
			microsoft: Boolean(env.MICROSOFT_CLIENT_ID),
			google: Boolean(env.GOOGLE_CLIENT_ID),
			github: Boolean(env.GITHUB_CLIENT_ID),
		},
	}, 200, origin);
}

async function handleListComments(request: Request, env: Env, origin: string): Promise<Response> {
	if (!env.COMMENTS_DB) return badConfig(origin);
	const slug = safeSlug(new URL(request.url).searchParams.get("slug"));
	if (!slug) return jsonResponse({ error: "Missing slug" }, 400, origin);
	const user = await getSessionUser(request, env);
	const { results } = await env.COMMENTS_DB.prepare(
		`SELECT id, parent_id, user_id, display_name, body, created_at
		 FROM comments
		 WHERE slug = ? AND status = 'approved'
		 ORDER BY COALESCE(parent_id, id) ASC, parent_id IS NOT NULL ASC, created_at ASC`,
	).bind(slug).all();
	const comments = (results || []).map((row: any) => {
		const isDeleted = row.body === "[deleted]";
		return {
			id: row.id,
			parent_id: row.parent_id,
			display_name: row.display_name,
			body: row.body,
			created_at: row.created_at,
			is_deleted: isDeleted,
			can_delete: Boolean(user?.id && row.user_id === user.id && !isDeleted),
		};
	});
	return jsonResponse({ comments }, 200, origin);
}

async function handleSession(request: Request, env: Env, origin: string): Promise<Response> {
	const user = await getSessionUser(request, env);
	if (!user) return jsonResponse({ authenticated: false }, 200, origin);
	return jsonResponse({
		authenticated: true,
		user: {
			name: user.display_name,
			email: user.email,
			provider: user.provider,
		},
	}, 200, origin);
}

async function handleCreateComment(request: Request, env: Env, origin: string): Promise<Response> {
	if (!env.COMMENTS_DB) return badConfig(origin);
	const user = await getSessionUser(request, env);
	if (!user) return jsonResponse({ error: "Sign in required" }, 401, origin);

	let payload: Record<string, unknown>;
	try {
		payload = (await request.json()) as Record<string, unknown>;
	} catch {
		return jsonResponse({ error: "Invalid JSON body" }, 400, origin);
	}

	const turnstileToken = String(payload.turnstileToken || "");
	if (!await validateTurnstile(turnstileToken, request, env)) {
		return jsonResponse({ error: "Human verification failed" }, 400, origin);
	}

	const slug = safeSlug(payload.slug);
	const body = safeComment(payload.body);
	const parentId = Number(payload.parentId || 0);
	if (!slug) return jsonResponse({ error: "Missing article slug" }, 400, origin);
	if (body.length < COMMENT_MIN_LENGTH) return jsonResponse({ error: "Comment is too short" }, 400, origin);

	let normalizedParentId: number | null = null;
	if (parentId > 0) {
		const parent = await env.COMMENTS_DB.prepare(
			`SELECT id, parent_id
			 FROM comments
			 WHERE id = ? AND slug = ? AND status = 'approved'`,
		).bind(parentId, slug).first<{ id: number; parent_id: number | null }>();

		if (!parent?.id) return jsonResponse({ error: "Reply target was not found" }, 400, origin);
		if (COMMENT_MAX_THREAD_DEPTH === 1 && parent.parent_id) {
			return jsonResponse({ error: "Replies can only be added to top-level comments" }, 400, origin);
		}
		normalizedParentId = parent.id;
	}

	await env.COMMENTS_DB.prepare(
		`INSERT INTO comments (slug, parent_id, user_id, provider, provider_user_id, display_name, email_hash, body, status, created_at, updated_at)
		 VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', datetime('now'), datetime('now'))`,
	).bind(
		slug,
		normalizedParentId,
		user.id,
		user.provider,
		user.provider_user_id,
		safeDisplayName(user.display_name) || "Verified reader",
		user.email_hash,
		body,
	).run();

	return jsonResponse({ ok: true, status: "pending" }, 201, origin);
}

async function handleDeleteComment(request: Request, env: Env, origin: string, id: number): Promise<Response> {
	if (!env.COMMENTS_DB) return badConfig(origin);
	const user = await getSessionUser(request, env);
	if (!user) return jsonResponse({ error: "Sign in required" }, 401, origin);
	if (!id) return jsonResponse({ error: "Missing comment id" }, 400, origin);

	const comment = await env.COMMENTS_DB.prepare(
		`SELECT id, user_id, parent_id
		 FROM comments
		 WHERE id = ? AND status = 'approved'`,
	).bind(id).first<{ id: number; user_id: number; parent_id: number | null }>();

	if (!comment?.id) return jsonResponse({ error: "Comment not found" }, 404, origin);
	if (comment.user_id !== user.id) return jsonResponse({ error: "You can only delete your own comments" }, 403, origin);

	if (!comment.parent_id) {
		const childCount = await env.COMMENTS_DB.prepare(
			"SELECT COUNT(*) AS count FROM comments WHERE parent_id = ? AND status = 'approved'",
		).bind(id).first<{ count: number }>();

		if (Number(childCount?.count || 0) > 0) {
			await env.COMMENTS_DB.prepare(
				`UPDATE comments
				 SET display_name = 'Deleted comment', body = '[deleted]', updated_at = datetime('now')
				 WHERE id = ?`,
			).bind(id).run();
			return jsonResponse({ ok: true, deleted: true, preservedThread: true }, 200, origin);
		}
	}

	await env.COMMENTS_DB.prepare("DELETE FROM comments WHERE id = ?").bind(id).run();
	return jsonResponse({ ok: true, deleted: true }, 200, origin);
}

function oauthStateCookie(state: string): string {
	return `oc_comment_state=${state}; Path=/comments/auth; HttpOnly; Secure; SameSite=Lax; Max-Age=600`;
}

function clearOauthStateCookie(): string {
	return "oc_comment_state=; Path=/comments/auth; HttpOnly; Secure; SameSite=Lax; Max-Age=0";
}

function readCookie(request: Request, name: string): string {
	const cookie = request.headers.get("Cookie") || "";
	for (const item of cookie.split(";")) {
		const [key, ...rest] = item.trim().split("=");
		if (key === name) return rest.join("=");
	}
	return "";
}

async function handleMicrosoftStart(request: Request, env: Env): Promise<Response> {
	if (!env.MICROSOFT_CLIENT_ID) return htmlResponse("Comments are not configured", 503);
	const url = new URL(request.url);
	const returnTo = url.searchParams.get("return_to");
	if (!isAllowedReturnUrl(returnTo)) return htmlResponse("Invalid return URL", 400);
	const state = randomToken(24);
	const stateValue = btoa(JSON.stringify({ state, returnTo }));
	const redirectUri = `${url.origin}/comments/auth/microsoft/callback`;
	const authUrl = new URL(`${MICROSOFT_AUTHORITY}/authorize`);
	authUrl.searchParams.set("client_id", env.MICROSOFT_CLIENT_ID);
	authUrl.searchParams.set("response_type", "code");
	authUrl.searchParams.set("redirect_uri", redirectUri);
	authUrl.searchParams.set("response_mode", "query");
	authUrl.searchParams.set("scope", "openid profile email User.Read");
	authUrl.searchParams.set("state", stateValue);
	authUrl.searchParams.set("prompt", "select_account");
	return redirectResponse(authUrl.toString(), { headers: { "Set-Cookie": oauthStateCookie(state) } });
}

async function handleGoogleStart(request: Request, env: Env): Promise<Response> {
	if (!env.GOOGLE_CLIENT_ID) return htmlResponse("Comments are not configured", 503);
	const url = new URL(request.url);
	const returnTo = url.searchParams.get("return_to");
	if (!isAllowedReturnUrl(returnTo)) return htmlResponse("Invalid return URL", 400);
	const state = randomToken(24);
	const stateValue = btoa(JSON.stringify({ state, returnTo }));
	const redirectUri = `${url.origin}/comments/auth/google/callback`;
	const authUrl = new URL(GOOGLE_AUTH_ENDPOINT);
	authUrl.searchParams.set("client_id", env.GOOGLE_CLIENT_ID);
	authUrl.searchParams.set("response_type", "code");
	authUrl.searchParams.set("redirect_uri", redirectUri);
	authUrl.searchParams.set("scope", "openid email profile");
	authUrl.searchParams.set("state", stateValue);
	authUrl.searchParams.set("prompt", "select_account");
	return redirectResponse(authUrl.toString(), { headers: { "Set-Cookie": oauthStateCookie(state) } });
}

async function handleGithubStart(request: Request, env: Env): Promise<Response> {
	if (!env.GITHUB_CLIENT_ID) return htmlResponse("Comments are not configured", 503);
	const url = new URL(request.url);
	const returnTo = url.searchParams.get("return_to");
	if (!isAllowedReturnUrl(returnTo)) return htmlResponse("Invalid return URL", 400);
	const state = randomToken(24);
	const stateValue = btoa(JSON.stringify({ state, returnTo }));
	const redirectUri = `${url.origin}/comments/auth/github/callback`;
	const authUrl = new URL(GITHUB_AUTH_ENDPOINT);
	authUrl.searchParams.set("client_id", env.GITHUB_CLIENT_ID);
	authUrl.searchParams.set("redirect_uri", redirectUri);
	authUrl.searchParams.set("scope", "read:user user:email");
	authUrl.searchParams.set("state", stateValue);
	authUrl.searchParams.set("prompt", "select_account");
	return redirectResponse(authUrl.toString(), { headers: { "Set-Cookie": oauthStateCookie(state) } });
}

function readOauthState(request: Request, encodedState: string): { returnTo: string } | Response {
	let statePayload: { state: string; returnTo: string };
	try {
		statePayload = JSON.parse(atob(encodedState));
	} catch {
		return htmlResponse("Invalid OAuth state", 400);
	}
	if (readCookie(request, "oc_comment_state") !== statePayload.state || !isAllowedReturnUrl(statePayload.returnTo)) {
		return htmlResponse("Invalid OAuth state", 400);
	}
	return { returnTo: statePayload.returnTo };
}

async function createSessionRedirect(request: Request, env: Env, returnTo: string, userId: number): Promise<Response> {
	if (!env.COMMENTS_DB || !env.COMMENT_SESSION_SECRET) return htmlResponse("Comments are not configured", 503);
	const sessionToken = randomToken(32);
	const tokenHash = await sha256Hex(`${env.COMMENT_SESSION_SECRET}:${sessionToken}`);
	await env.COMMENTS_DB.prepare(
		`INSERT INTO comment_sessions (token_hash, user_id, created_at, expires_at)
		 VALUES (?, ?, datetime('now'), datetime('now', ?))`,
	).bind(tokenHash, userId, `+${COMMENT_SESSION_TTL_SECONDS} seconds`).run();

	const returnUrl = new URL(returnTo);
	returnUrl.hash = `oc_comment_token=${encodeURIComponent(sessionToken)}`;
	return redirectResponse(returnUrl.toString(), {
		headers: { "Set-Cookie": clearOauthStateCookie() },
	});
}

async function upsertMicrosoftUser(env: Env, profile: any): Promise<number> {
	if (!env.COMMENTS_DB) throw new Error("D1 not configured");
	const email = String(profile.mail || profile.userPrincipalName || "").toLowerCase();
	const emailHash = await sha256Hex(email);
	const providerUserId = String(profile.id || emailHash);
	const displayName = safeDisplayName(profile.displayName || email || "Microsoft user");
	const existing = await env.COMMENTS_DB.prepare(
		"SELECT id FROM comment_users WHERE provider = 'microsoft' AND provider_user_id = ?",
	).bind(providerUserId).first<{ id: number }>();

	if (existing?.id) {
		await env.COMMENTS_DB.prepare(
			`UPDATE comment_users
			 SET display_name = ?, email = ?, email_hash = ?, updated_at = datetime('now')
			 WHERE id = ?`,
		).bind(displayName, email, emailHash, existing.id).run();
		return existing.id;
	}

	const result = await env.COMMENTS_DB.prepare(
		`INSERT INTO comment_users (provider, provider_user_id, display_name, email, email_hash, created_at, updated_at)
		 VALUES ('microsoft', ?, ?, ?, ?, datetime('now'), datetime('now'))`,
	).bind(providerUserId, displayName, email, emailHash).run();
	return Number(result.meta.last_row_id);
}

async function upsertOAuthUser(env: Env, provider: string, providerUserId: string, displayName: string, email: string): Promise<number> {
	if (!env.COMMENTS_DB) throw new Error("D1 not configured");
	const normalizedEmail = email.toLowerCase();
	const emailHash = await sha256Hex(normalizedEmail);
	const safeName = safeDisplayName(displayName || normalizedEmail || `${provider} user`);
	const existing = await env.COMMENTS_DB.prepare(
		"SELECT id FROM comment_users WHERE provider = ? AND provider_user_id = ?",
	).bind(provider, providerUserId).first<{ id: number }>();

	if (existing?.id) {
		await env.COMMENTS_DB.prepare(
			`UPDATE comment_users
			 SET display_name = ?, email = ?, email_hash = ?, updated_at = datetime('now')
			 WHERE id = ?`,
		).bind(safeName, normalizedEmail, emailHash, existing.id).run();
		return existing.id;
	}

	const result = await env.COMMENTS_DB.prepare(
		`INSERT INTO comment_users (provider, provider_user_id, display_name, email, email_hash, created_at, updated_at)
		 VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))`,
	).bind(provider, providerUserId, safeName, normalizedEmail, emailHash).run();
	return Number(result.meta.last_row_id);
}

async function handleMicrosoftCallback(request: Request, env: Env): Promise<Response> {
	if (!env.COMMENTS_DB || !env.MICROSOFT_CLIENT_ID || !env.MICROSOFT_CLIENT_SECRET || !env.COMMENT_SESSION_SECRET) {
		return htmlResponse("Comments are not configured", 503);
	}

	const url = new URL(request.url);
	const code = url.searchParams.get("code");
	const encodedState = url.searchParams.get("state") || "";
	if (!code || !encodedState) return htmlResponse("Missing OAuth response", 400);

	const stateResult = readOauthState(request, encodedState);
	if (stateResult instanceof Response) return stateResult;

	const redirectUri = `${url.origin}/comments/auth/microsoft/callback`;
	const tokenResponse = await fetch(`${MICROSOFT_AUTHORITY}/token`, {
		method: "POST",
		headers: { "Content-Type": "application/x-www-form-urlencoded" },
		body: new URLSearchParams({
			client_id: env.MICROSOFT_CLIENT_ID,
			client_secret: env.MICROSOFT_CLIENT_SECRET,
			grant_type: "authorization_code",
			code,
			redirect_uri: redirectUri,
			scope: "openid profile email User.Read",
		}),
	});
	const tokenData = await tokenResponse.json().catch(() => null) as any;
	if (!tokenResponse.ok || !tokenData?.access_token) {
		return htmlResponse("Microsoft sign-in failed", 502);
	}

	const profileResponse = await fetch(GRAPH_ME_ENDPOINT, {
		headers: { Authorization: `Bearer ${tokenData.access_token}` },
	});
	const profile = await profileResponse.json().catch(() => null) as any;
	if (!profileResponse.ok || !profile) return htmlResponse("Could not read Microsoft profile", 502);

	const userId = await upsertMicrosoftUser(env, profile);
	return createSessionRedirect(request, env, stateResult.returnTo, userId);
}

async function handleGoogleCallback(request: Request, env: Env): Promise<Response> {
	if (!env.GOOGLE_CLIENT_ID || !env.GOOGLE_CLIENT_SECRET) return htmlResponse("Comments are not configured", 503);
	const url = new URL(request.url);
	const code = url.searchParams.get("code");
	const encodedState = url.searchParams.get("state") || "";
	if (!code || !encodedState) return htmlResponse("Missing OAuth response", 400);
	const stateResult = readOauthState(request, encodedState);
	if (stateResult instanceof Response) return stateResult;

	const redirectUri = `${url.origin}/comments/auth/google/callback`;
	const tokenResponse = await fetch(GOOGLE_TOKEN_ENDPOINT, {
		method: "POST",
		headers: { "Content-Type": "application/x-www-form-urlencoded" },
		body: new URLSearchParams({
			client_id: env.GOOGLE_CLIENT_ID,
			client_secret: env.GOOGLE_CLIENT_SECRET,
			grant_type: "authorization_code",
			code,
			redirect_uri: redirectUri,
		}),
	});
	const tokenData = await tokenResponse.json().catch(() => null) as any;
	if (!tokenResponse.ok || !tokenData?.access_token) return htmlResponse("Google sign-in failed", 502);

	const profileResponse = await fetch(GOOGLE_USERINFO_ENDPOINT, {
		headers: { Authorization: `Bearer ${tokenData.access_token}` },
	});
	const profile = await profileResponse.json().catch(() => null) as any;
	if (!profileResponse.ok || !profile?.sub || !profile?.email || profile.email_verified !== true) {
		return htmlResponse("Could not verify Google email", 502);
	}
	const userId = await upsertOAuthUser(env, "google", String(profile.sub), String(profile.name || profile.email), String(profile.email));
	return createSessionRedirect(request, env, stateResult.returnTo, userId);
}

async function handleGithubCallback(request: Request, env: Env): Promise<Response> {
	if (!env.GITHUB_CLIENT_ID || !env.GITHUB_CLIENT_SECRET) return htmlResponse("Comments are not configured", 503);
	const url = new URL(request.url);
	const code = url.searchParams.get("code");
	const encodedState = url.searchParams.get("state") || "";
	if (!code || !encodedState) return htmlResponse("Missing OAuth response", 400);
	const stateResult = readOauthState(request, encodedState);
	if (stateResult instanceof Response) return stateResult;

	const redirectUri = `${url.origin}/comments/auth/github/callback`;
	const tokenResponse = await fetch(GITHUB_TOKEN_ENDPOINT, {
		method: "POST",
		headers: { "Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded" },
		body: new URLSearchParams({
			client_id: env.GITHUB_CLIENT_ID,
			client_secret: env.GITHUB_CLIENT_SECRET,
			code,
			redirect_uri: redirectUri,
		}),
	});
	const tokenData = await tokenResponse.json().catch(() => null) as any;
	if (!tokenResponse.ok || !tokenData?.access_token) return htmlResponse("GitHub sign-in failed", 502);
	const githubHeaders = {
		"Accept": "application/vnd.github+json",
		"Authorization": `Bearer ${tokenData.access_token}`,
		"User-Agent": "OceanCloud-Comments",
		"X-GitHub-Api-Version": "2022-11-28",
	};
	const [profileResponse, emailsResponse] = await Promise.all([
		fetch(GITHUB_USER_ENDPOINT, { headers: githubHeaders }),
		fetch(GITHUB_EMAILS_ENDPOINT, { headers: githubHeaders }),
	]);
	const profile = await profileResponse.json().catch(() => null) as any;
	const emails = await emailsResponse.json().catch(() => null) as any[] | null;
	const primaryEmail = Array.isArray(emails)
		? emails.find((item) => item?.primary && item?.verified)?.email || emails.find((item) => item?.verified)?.email
		: "";
	if (!profileResponse.ok || !profile?.id || !primaryEmail) return htmlResponse("Could not verify GitHub email", 502);
	const name = String(profile.name || profile.login || primaryEmail);
	const userId = await upsertOAuthUser(env, "github", String(profile.id), name, String(primaryEmail));
	return createSessionRedirect(request, env, stateResult.returnTo, userId);
}

function requireAdmin(request: Request, env: Env): boolean {
	return Boolean(env.ADMIN_TOKEN && getAdminToken(request) === env.ADMIN_TOKEN);
}

async function handleAdminList(request: Request, env: Env, origin: string): Promise<Response> {
	if (!env.COMMENTS_DB) return badConfig(origin);
	if (!requireAdmin(request, env)) return jsonResponse({ error: "Unauthorized" }, 401, origin);
	const status = new URL(request.url).searchParams.get("status") || "pending";
	const { results } = await env.COMMENTS_DB.prepare(
		`SELECT id, parent_id, slug, display_name, body, status, created_at, updated_at
		 FROM comments
		 WHERE status = ?
		 ORDER BY created_at DESC
		 LIMIT 100`,
	).bind(status).all();
	return jsonResponse({ comments: results || [] }, 200, origin);
}

async function handleAdminModerate(request: Request, env: Env, origin: string): Promise<Response> {
	if (!env.COMMENTS_DB) return badConfig(origin);
	if (!requireAdmin(request, env)) return jsonResponse({ error: "Unauthorized" }, 401, origin);
	const payload = await request.json().catch(() => null) as any;
	const id = Number(payload?.id || 0);
	const action = String(payload?.action || "");
	if (id && action === "delete") {
		await env.COMMENTS_DB.prepare("DELETE FROM comments WHERE parent_id = ?").bind(id).run();
		await env.COMMENTS_DB.prepare("DELETE FROM comments WHERE id = ?").bind(id).run();
		return jsonResponse({ ok: true, status: "deleted" }, 200, origin);
	}
	const status = action === "approve" ? "approved" : action === "reject" ? "rejected" : "";
	if (!id || !status) return jsonResponse({ error: "Invalid moderation action" }, 400, origin);
	await env.COMMENTS_DB.prepare(
		"UPDATE comments SET status = ?, updated_at = datetime('now') WHERE id = ?",
	).bind(status, id).run();
	return jsonResponse({ ok: true, status }, 200, origin);
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
		const url = new URL(request.url);

		if (request.method === "GET" && url.pathname === "/comments/auth/microsoft/start") {
			return handleMicrosoftStart(request, env);
		}

		if (request.method === "GET" && url.pathname === "/comments/auth/microsoft/callback") {
			return handleMicrosoftCallback(request, env);
		}

		if (request.method === "GET" && url.pathname === "/comments/auth/google/start") {
			return handleGoogleStart(request, env);
		}

		if (request.method === "GET" && url.pathname === "/comments/auth/google/callback") {
			return handleGoogleCallback(request, env);
		}

		if (request.method === "GET" && url.pathname === "/comments/auth/github/start") {
			return handleGithubStart(request, env);
		}

		if (request.method === "GET" && url.pathname === "/comments/auth/github/callback") {
			return handleGithubCallback(request, env);
		}

		const origin = request.headers.get("Origin");
		if (!isAllowedOrigin(origin)) {
			return new Response("Forbidden", { status: 403 });
		}

		if (request.method === "OPTIONS") {
			return new Response(null, { status: 204, headers: corsHeaders(origin) });
		}

		if (request.method === "GET" && url.pathname === "/") {
			return jsonResponse({ ok: true, service: "OceanCloud AI proxy" }, 200, origin);
		}

		if (url.pathname === "/comments/config" && request.method === "GET") {
			return handleCommentsConfig(env, origin);
		}

		if (url.pathname === "/comments" && request.method === "GET") {
			return handleListComments(request, env, origin);
		}

		if (url.pathname === "/comments/session" && request.method === "GET") {
			return handleSession(request, env, origin);
		}

		if (url.pathname === "/comments" && request.method === "POST") {
			return handleCreateComment(request, env, origin);
		}

		if (url.pathname.startsWith("/comments/") && request.method === "DELETE") {
			const id = Number(url.pathname.split("/").pop() || 0);
			return handleDeleteComment(request, env, origin, id);
		}

		if (url.pathname === "/comments/admin" && request.method === "GET") {
			return handleAdminList(request, env, origin);
		}

		if (url.pathname === "/comments/admin/moderate" && request.method === "POST") {
			return handleAdminModerate(request, env, origin);
		}

		if (request.method !== "POST" || !["/", "/chat"].includes(url.pathname)) {
			return jsonResponse({ error: "Not found" }, 404, origin);
		}

		return handleChat(request, env, origin);
	},
} satisfies ExportedHandler<Env>;
