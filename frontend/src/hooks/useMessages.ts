import { useCallback, useRef, useState } from "react";

import type { AlertVariant } from "../components/ui/Alert.tsx";

export interface PageMessage {
    id: number;
    variant: AlertVariant;
    text: string;
}

export interface NewMessage {
    variant: AlertVariant;
    text: string;
}

let nextId = 0;

// Action-scoped message queue (equivalent to Django's messages framework, but tied to one
// user action at a time instead of accumulating forever): call beginAction() when a new
// attempt starts — this clears whatever the previous action left behind and returns a token —
// then call replaceMessages() once that attempt's outcome is known, with every message it
// produced (zero, one, or several of different variants). A replaceMessages() call carrying a
// token from an action that is no longer the current one (a late response from an older,
// already-superseded submission) is ignored, so it can never resurrect stale notifications.
export function useMessages() {
    const [messages, setMessages] = useState<PageMessage[]>([]);
    const actionRef = useRef(0);

    const beginAction = useCallback((): number => {
        actionRef.current += 1;
        setMessages([]);
        return actionRef.current;
    }, []);

    const replaceMessages = useCallback((action: number, next: NewMessage[]) => {
        if (action !== actionRef.current) {
            return;
        }
        setMessages(next.map((message) => ({ id: (nextId += 1), ...message })));
    }, []);

    const dismissMessage = useCallback((id: number) => {
        setMessages((current) => current.filter((item) => item.id !== id));
    }, []);

    return { messages, beginAction, replaceMessages, dismissMessage };
}
