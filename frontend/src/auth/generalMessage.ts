import type { Translations } from "../i18n/types.ts";

// Uma mensagem geral do formulário guardada como estrutura (o "evento" que aconteceu),
// nunca como texto já resolvido: o texto exibido é calculado a cada render a partir do
// idioma atual, para acompanhar a troca de idioma sem precisar de uma nova ação/requisição.
export type GeneralMessage =
    // Erro geral da API com um "code" reconhecido (ex.: LoginForm): o texto vem do i18n do
    // próprio front, para não depender do idioma em que o Django respondeu a requisição.
    | { kind: "known-code"; code: KnownCode }
    // Erro geral da API sem "code" reconhecido: exibe o texto que o backend mandou. Fica
    // preso ao idioma da resposta até um novo envio, mas é o único texto disponível.
    | { kind: "backend-text"; text: string }
    | { kind: "network" }
    | { kind: "too-many-requests" }
    | { kind: "generic" };

type KnownCode = "invalid_login" | "inactive" | "email_not_verified";

const KNOWN_CODES: ReadonlySet<string> = new Set<KnownCode>([
    "invalid_login",
    "inactive",
    "email_not_verified",
]);

function isKnownCode(code: string): code is KnownCode {
    return KNOWN_CODES.has(code);
}

// A partir do que a API respondeu, decide se dá para exibir uma mensagem sempre traduzível
// (code conhecido) ou se sobra só o texto que a API já mandou traduzido.
export function generalMessagesFromApi(
    general: string[],
    code: string | undefined,
): GeneralMessage[] {
    if (code !== undefined && isKnownCode(code)) {
        return [{ kind: "known-code", code }];
    }

    return general.map((text) => ({ kind: "backend-text", text }));
}

export function resolveGeneralMessage(
    message: GeneralMessage,
    t: Translations,
): string {
    switch (message.kind) {
        case "known-code":
            return {
                invalid_login: t.auth.errors.invalidLogin,
                inactive: t.auth.errors.inactive,
                email_not_verified: t.auth.errors.emailNotVerified,
            }[message.code];
        case "backend-text":
            return message.text;
        case "network":
            return t.auth.errors.network;
        case "too-many-requests":
            return t.auth.errors.tooManyRequests;
        case "generic":
            return t.auth.errors.generic;
    }
}
