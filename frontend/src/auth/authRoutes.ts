const AUTH_PREFIXES = [
    "/login",
    "/signup",
    "/password-reset",
    "/email-verification",
    "/logged-out",
];

export function isAuthPath(pathname: string): boolean {
    return AUTH_PREFIXES.some((prefix) => pathname.startsWith(prefix));
}

// Monta um link preservando o `next` (quando existe) entre as páginas do fluxo.
export function withNext(path: string, next: string): string {
    return next ? `${path}?next=${encodeURIComponent(next)}` : path;
}
