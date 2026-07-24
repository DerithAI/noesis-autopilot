/**
 * Typed API fetch helper with retry + proper error type.
 *
 * Retry policy:
 *  - up to 2 retries (3 attempts total)
 *  - exponential backoff: 500ms, then 1500ms
 *  - only retries on network errors or 5xx responses
 *  - never retries POST unless `idempotent: true` is passed
 */

export const API_BASE: string = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export class ApiError extends Error {
  readonly status: number;
  readonly statusText: string;
  /** Parsed response body if it was JSON, raw text otherwise (may be undefined). */
  readonly body: unknown;

  constructor(status: number, statusText: string, body: unknown, path: string) {
    super(`API ${status} ${statusText} on ${path}`);
    this.name = 'ApiError';
    this.status = status;
    this.statusText = statusText;
    this.body = body;
  }
}

export interface ApiFetchOptions extends RequestInit {
  /**
   * Marks a non-GET request as safe to retry. POST requests are never
   * retried unless this flag is set.
   */
  idempotent?: boolean;
}

const MAX_RETRIES = 2;
const BACKOFF_MS = [500, 1500];

const sleep = (ms: number) => new Promise<void>((resolve) => setTimeout(resolve, ms));

function parseBody(text: string): unknown {
  if (!text) return undefined;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

/**
 * Fetch `API_BASE + path`, parse the JSON body and return it typed as `T`.
 *
 * Throws `ApiError` for non-2xx responses; rethrows network errors
 * (after exhausting retries where the retry policy allows).
 */
export async function apiFetch<T = unknown>(path: string, init?: ApiFetchOptions): Promise<T> {
  const { idempotent, ...fetchInit } = init ?? {};
  const method = (fetchInit.method ?? 'GET').toUpperCase();
  const canRetry = method !== 'POST' || idempotent === true;

  let lastError: unknown;

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    if (attempt > 0) {
      await sleep(BACKOFF_MS[attempt - 1]);
    }

    let res: Response;
    try {
      res = await fetch(`${API_BASE}${path}`, fetchInit);
    } catch (err) {
      // Network error (server down, DNS, CORS...) — retryable if policy allows.
      lastError = err;
      if (canRetry && attempt < MAX_RETRIES) continue;
      throw err;
    }

    if (!res.ok) {
      const error = new ApiError(res.status, res.statusText, parseBody(await res.text()), path);
      // Only 5xx is retryable; 4xx is a definitive answer.
      if (res.status >= 500 && canRetry && attempt < MAX_RETRIES) {
        lastError = error;
        continue;
      }
      throw error;
    }

    return parseBody(await res.text()) as T;
  }

  // Unreachable, but satisfies the compiler.
  throw lastError;
}
