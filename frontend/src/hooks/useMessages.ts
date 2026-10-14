import { useCallback, useState } from "react";

import type { AlertVariant } from "../components/ui/Alert.tsx";

export interface PageMessage {
    id: number;
    variant: AlertVariant;
    text: string;
}

let nextId = 0;

// Equivalente ao framework de mensagens do Django (messages.success/error/...), mas em
// memória no componente: cada página autenticada decide quando empilhar uma mensagem,
// e o layout só precisa saber renderizá-las e permitir dispensar.
export function useMessages() {
    const [messages, setMessages] = useState<PageMessage[]>([]);

    const addMessage = useCallback((variant: AlertVariant, text: string) => {
        nextId += 1;
        setMessages((current) => [...current, { id: nextId, variant, text }]);
    }, []);

    const dismissMessage = useCallback((id: number) => {
        setMessages((current) => current.filter((item) => item.id !== id));
    }, []);

    return { messages, addMessage, dismissMessage };
}
