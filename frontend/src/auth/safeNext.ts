const PLACEHOLDER_ORIGIN = "http://next.invalid";

// O `next` só pode ser um caminho interno ("/checkout?x=1"): qualquer coisa que resolva
// para outra origem (URL absoluta, "//host", "/\host", "javascript:") é descartada,
// evitando open redirect. Devolve "" quando não é seguro.
export function safeNext(value: string | null): string {
    if (!value?.startsWith("/") || value.startsWith("//")) {
        return "";
    }

    if (value.includes("\\")) {
        return "";
    }

    try {
        return new URL(value, PLACEHOLDER_ORIGIN).origin === PLACEHOLDER_ORIGIN
            ? value
            : "";
    } catch {
        return "";
    }
}
