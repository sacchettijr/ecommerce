import { useState } from "react";
import type { ChangeEvent } from "react";

import { ApiError } from "../api/client.ts";
import { parseFormErrors } from "../api/formErrors.ts";
import type { GeneralMessage } from "../auth/generalMessage.ts";
import {
    generalMessagesFromApi,
    resolveGeneralMessage,
} from "../auth/generalMessage.ts";
import { useLanguage } from "../i18n/useLanguage.ts";

// Estado comum dos formulários que falam com a API: valores, erros por campo,
// erros gerais do formulário e "enviando" (evita submits duplicados).
export function useApiForm<V extends Record<string, string>>(initial: V) {
    const { t } = useLanguage();
    const [values, setValues] = useState<V>(initial);
    const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
    // Guardado como estrutura, não como texto: resolvido para o idioma atual a cada render
    // (ver generalErrors abaixo), então uma troca de idioma atualiza a mensagem já visível.
    const [generalMessages, setGeneralMessages] = useState<GeneralMessage[]>(
        [],
    );
    const [code, setCode] = useState<string | undefined>(undefined);
    const [submitting, setSubmitting] = useState(false);

    const onChange = (event: ChangeEvent<HTMLInputElement>) => {
        const { name, value } = event.target;
        setValues((current) => ({ ...current, [name]: value }));
    };

    const clearErrors = () => {
        setFieldErrors({});
        setGeneralMessages([]);
        setCode(undefined);
    };

    // Executa a chamada; devolve true se deu certo. Erros 400 da API viram erros
    // de campo/gerais, sem serem achatados numa mensagem genérica.
    const submit = async (action: () => Promise<void>): Promise<boolean> => {
        if (submitting) {
            return false;
        }

        clearErrors();
        setSubmitting(true);

        try {
            await action();
            return true;
        } catch (error) {
            if (error instanceof ApiError && error.status === 400) {
                const parsed = parseFormErrors(error.data);
                setFieldErrors(parsed.fields);
                setGeneralMessages(
                    generalMessagesFromApi(parsed.general, parsed.code),
                );
                setCode(parsed.code);
            } else if (error instanceof ApiError && error.status === 429) {
                setGeneralMessages([{ kind: "too-many-requests" }]);
            } else if (error instanceof ApiError) {
                setGeneralMessages([{ kind: "generic" }]);
            } else {
                setGeneralMessages([{ kind: "network" }]);
            }

            return false;
        } finally {
            setSubmitting(false);
        }
    };

    return {
        values,
        onChange,
        fieldErrors,
        generalErrors: generalMessages.map((message) =>
            resolveGeneralMessage(message, t),
        ),
        code,
        submitting,
        submit,
    };
}
