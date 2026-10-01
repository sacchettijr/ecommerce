const API_URL: string = (import.meta.env.VITE_API_URL ?? "/api").replace(
    /\/$/,
    "",
);

const LANGUAGE_STORAGE_KEY = "language";

export class ApiError extends Error {
    status: number;
    data: unknown;

    constructor(status: number, data: unknown) {
        super(`HTTP ${status}`);
        this.name = "ApiError";
        this.status = status;
        this.data = data;
    }
}

function readCookie(name: string): string | null {
    const prefix = `${name}=`;
    const entry = document.cookie
        .split("; ")
        .find((item) => item.startsWith(prefix));

    return entry ? decodeURIComponent(entry.slice(prefix.length)) : null;
}

// O Django manda o cookie CSRF no endpoint de sessão; se ele ainda não chegou
// (primeiro POST antes do carregamento inicial), busca-o antes de escrever.
async function csrfToken(): Promise<string> {
    const existing = readCookie("csrftoken");

    if (existing) {
        return existing;
    }

    await fetch(`${API_URL}/account/session/`, { credentials: "include" });

    return readCookie("csrftoken") ?? "";
}

function currentLanguage(): string | null {
    try {
        return localStorage.getItem(LANGUAGE_STORAGE_KEY);
    } catch {
        return null;
    }
}

function parseBody(text: string): unknown {
    if (!text) {
        return null;
    }

    try {
        return JSON.parse(text);
    } catch {
        return null;
    }
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
    const language = currentLanguage();
    const isWrite = init.method !== "GET";

    const response = await fetch(`${API_URL}${path}`, {
        ...init,
        credentials: "include",
        headers: {
            Accept: "application/json",
            // As mensagens de validação do Django saem no idioma escolhido no site.
            ...(language ? { "Accept-Language": language } : {}),
            ...(isWrite ? { "X-CSRFToken": await csrfToken() } : {}),
            ...init.headers,
        },
    });

    const data = parseBody(await response.text());

    if (!response.ok) {
        throw new ApiError(response.status, data);
    }

    return data as T;
}

export function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
    return request<T>(path, { method: "GET", signal });
}

export function apiPost<T>(
    path: string,
    body: unknown,
    signal?: AbortSignal,
): Promise<T> {
    return request<T>(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal,
    });
}
