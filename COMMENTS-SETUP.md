# OceanCloud Comments Setup

This site uses the existing Cloudflare Worker in `oceancloud-ai-proxy/` for comments.

Comments are deliberately moderated:

1. Reader signs in with Microsoft.
2. Reader completes Cloudflare Turnstile.
3. Comment is stored in D1 as `pending`.
4. Admin approves or rejects from `comments-admin.html`.
5. Only approved comments display publicly.

## Cloudflare Resources

Create the D1 database:

```powershell
cd oceancloud-ai-proxy
npx wrangler d1 create oceancloud-comments
```

Copy the `database_id` returned by Wrangler into `wrangler.jsonc` under the `COMMENTS_DB` binding if Wrangler does not write it automatically.

Apply the schema locally for testing:

```powershell
npx wrangler d1 migrations apply oceancloud-comments --local
```

Apply the schema to production:

```powershell
npx wrangler d1 migrations apply oceancloud-comments --remote
```

Create a Cloudflare Turnstile widget for `oceancloudconsults.com`, then set secrets:

```powershell
npx wrangler secret put TURNSTILE_SECRET_KEY
```

Set `TURNSTILE_SITE_KEY` as a non-secret variable in the Worker dashboard, or add it as a secret if you prefer:

```powershell
npx wrangler secret put TURNSTILE_SITE_KEY
```

## Microsoft OAuth App

Create an app registration in Microsoft Entra admin center.

Use this redirect URI:

```text
https://oceancloud-ai-proxy.oceancloud-ai-proxy.workers.dev/comments/auth/microsoft/callback
```

Supported account types:

```text
Accounts in any organizational directory and personal Microsoft accounts
```

API permissions:

```text
Microsoft Graph delegated: User.Read
OpenID scopes requested by the app: openid profile email
```

Create a client secret, then set Worker secrets:

```powershell
npx wrangler secret put MICROSOFT_CLIENT_ID
npx wrangler secret put MICROSOFT_CLIENT_SECRET
npx wrangler secret put COMMENT_SESSION_SECRET
npx wrangler secret put ADMIN_TOKEN
```

`COMMENT_SESSION_SECRET` and `ADMIN_TOKEN` should be long random values.

## Deploy

```powershell
cd oceancloud-ai-proxy
npm test -- --run
npx tsc --noEmit
npm run deploy
```

## Moderate Comments

Open:

```text
https://oceancloudconsults.com/comments-admin.html
```

Paste the `ADMIN_TOKEN` value. Pending comments are loaded from the Worker and can be approved or rejected.

## Frontend

Every file under `articles/` loads:

```html
<script src="../js/comments.js?v=1"></script>
```

The script injects the comments block before related guides and loads `css/comments.css?v=1` dynamically.
