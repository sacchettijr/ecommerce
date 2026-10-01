export interface FormErrors {
    // Erros de campo, já unidos numa única mensagem por campo.
    fields: Record<string, string>;
    // Erros gerais do formulário (non_field_errors).
    general: string[];
    // Código do erro geral (ex.: "email_not_verified" ou "invalid_link").
    code?: string;
}

function messages(value: unknown): string[] {
    if (typeof value === "string") {
        return [value];
    }

    return Array.isArray(value)
        ? value.filter((item): item is string => typeof item === "string")
        : [];
}

// Formato do backend: { "<campo>": ["msg"], "non_field_errors": ["msg"], "code": "..." }
export function parseFormErrors(data: unknown): FormErrors {
    const result: FormErrors = { fields: {}, general: [] };

    if (typeof data !== "object" || data === null) {
        return result;
    }

    for (const [key, value] of Object.entries(data)) {
        if (key === "code") {
            if (typeof value === "string") {
                result.code = value;
            }
        } else if (key === "non_field_errors" || key === "detail") {
            result.general.push(...messages(value));
        } else {
            const text = messages(value).join(" ");

            if (text) {
                result.fields[key] = text;
            }
        }
    }

    return result;
}
