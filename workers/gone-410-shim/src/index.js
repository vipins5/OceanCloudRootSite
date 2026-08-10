/**
 * Rewrites 404s under /mc/MC* and /articles/news-* to 410 Gone.
 *
 * GitHub Pages (the static origin) can only ever return 404 for a missing
 * file. These two path families are where OceanCloud's mass-published
 * Message Center / auto-news pages used to live; large batches of them were
 * deliberately removed to recover from a Google scaled-content trust hit.
 * A 410 tells Google "this is permanently gone, stop rechecking it" instead
 * of the weaker, ambiguous 404 ("might come back"), which is the faster
 * signal for getting stale URLs dropped from consideration.
 *
 * Anything that still exists at origin (current MC utility pages, the /mc
 * index, etc.) passes through unchanged -- only a 404 response gets
 * remapped.
 */

const GONE_PATTERNS = [/^\/mc\/MC\d+(\.html)?$/i, /^\/articles\/news-/i];

export default {
	async fetch(request) {
		const { pathname } = new URL(request.url);
		const isGoneCandidate = GONE_PATTERNS.some((re) => re.test(pathname));

		const originResponse = await fetch(request);

		if (isGoneCandidate && originResponse.status === 404) {
			return new Response(originResponse.body, {
				status: 410,
				statusText: "Gone",
				headers: originResponse.headers,
			});
		}

		return originResponse;
	},
};
