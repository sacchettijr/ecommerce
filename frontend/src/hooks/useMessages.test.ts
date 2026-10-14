import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useMessages } from "./useMessages.ts";

describe("useMessages", () => {
    it("starts empty", () => {
        const { result } = renderHook(() => useMessages());

        expect(result.current.messages).toEqual([]);
    });

    it("replaceMessages shows every message an action produced, including multiple variants at once", () => {
        const { result } = renderHook(() => useMessages());

        let token = 0;
        act(() => {
            token = result.current.beginAction();
        });
        act(() => {
            result.current.replaceMessages(token, [
                { variant: "warning", text: "Watch out" },
                { variant: "error", text: "Also broken" },
            ]);
        });

        expect(result.current.messages.map((m) => [m.variant, m.text])).toEqual([
            ["warning", "Watch out"],
            ["error", "Also broken"],
        ]);
    });

    it("a new action replaces notifications left by a previous action", () => {
        const { result } = renderHook(() => useMessages());

        let firstToken = 0;
        act(() => {
            firstToken = result.current.beginAction();
        });
        act(() => {
            result.current.replaceMessages(firstToken, [
                { variant: "success", text: "First action succeeded" },
            ]);
        });
        expect(result.current.messages).toHaveLength(1);

        let secondToken = 0;
        act(() => {
            secondToken = result.current.beginAction();
        });
        // Nothing shown yet for the new action: the old one must already be gone.
        expect(result.current.messages).toEqual([]);

        act(() => {
            result.current.replaceMessages(secondToken, [
                { variant: "success", text: "Second action succeeded" },
            ]);
        });

        expect(result.current.messages).toHaveLength(1);
        expect(result.current.messages[0]?.text).toBe("Second action succeeded");
    });

    it("two consecutive successful actions never leave duplicate stale success messages", () => {
        const { result } = renderHook(() => useMessages());

        for (let i = 0; i < 2; i += 1) {
            let token = 0;
            act(() => {
                token = result.current.beginAction();
            });
            act(() => {
                result.current.replaceMessages(token, [
                    { variant: "success", text: "Changed successfully" },
                ]);
            });
        }

        expect(result.current.messages).toHaveLength(1);
    });

    it("a warning from a later action removes an earlier success message", () => {
        const { result } = renderHook(() => useMessages());

        let successToken = 0;
        act(() => {
            successToken = result.current.beginAction();
        });
        act(() => {
            result.current.replaceMessages(successToken, [
                { variant: "success", text: "Changed successfully" },
            ]);
        });

        let warningToken = 0;
        act(() => {
            warningToken = result.current.beginAction();
        });
        act(() => {
            result.current.replaceMessages(warningToken, [
                { variant: "warning", text: "Nothing changed" },
            ]);
        });

        expect(result.current.messages).toHaveLength(1);
        expect(result.current.messages[0]).toMatchObject({
            variant: "warning",
            text: "Nothing changed",
        });
    });

    it("a field-error-only action (no general message) still clears a previous success message", () => {
        const { result } = renderHook(() => useMessages());

        let successToken = 0;
        act(() => {
            successToken = result.current.beginAction();
        });
        act(() => {
            result.current.replaceMessages(successToken, [
                { variant: "success", text: "Changed successfully" },
            ]);
        });

        act(() => {
            // The next action only produced a field-level error, so it has no messages of its
            // own for the shared area — but starting it must still have cleared the old one.
            result.current.beginAction();
        });

        expect(result.current.messages).toEqual([]);
    });

    it("dismissing one message does not remove the others from the same action", () => {
        const { result } = renderHook(() => useMessages());

        let token = 0;
        act(() => {
            token = result.current.beginAction();
        });
        act(() => {
            result.current.replaceMessages(token, [
                { variant: "warning", text: "Watch out" },
                { variant: "error", text: "Also broken" },
            ]);
        });
        const idToDismiss = result.current.messages[0]?.id;

        act(() => {
            if (idToDismiss !== undefined) {
                result.current.dismissMessage(idToDismiss);
            }
        });

        expect(result.current.messages).toHaveLength(1);
        expect(result.current.messages[0]?.text).toBe("Also broken");
    });

    it("an older action's late response cannot resurrect stale notifications after a newer action started", () => {
        const { result } = renderHook(() => useMessages());

        let staleToken = 0;
        act(() => {
            staleToken = result.current.beginAction();
        });

        // A newer action starts before the older one's response comes back.
        act(() => {
            result.current.beginAction();
        });

        act(() => {
            // The stale, superseded action's response finally resolves — it must be ignored.
            result.current.replaceMessages(staleToken, [
                { variant: "error", text: "Stale error from an old request" },
            ]);
        });

        expect(result.current.messages).toEqual([]);
    });
});
