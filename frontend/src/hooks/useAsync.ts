import { useEffect, useState } from "react";

interface AsyncState<A, T> {
    arg: A;
    data?: T;
    error?: unknown;
}

export function useAsync<A, T>(
    fn: (arg: A, signal: AbortSignal) => Promise<T>,
    arg: A,
) {
    const [state, setState] = useState<AsyncState<A, T> | null>(null);

    useEffect(() => {
        const controller = new AbortController();

        fn(arg, controller.signal)
            .then((data) => setState({ arg, data }))
            .catch((error: unknown) => {
                if (!controller.signal.aborted) {
                    setState({ arg, error });
                }
            });

        return () => controller.abort();
    }, [fn, arg]);

    const settled = state !== null && state.arg === arg;

    return {
        data: settled ? state.data : undefined,
        error: settled ? state.error : undefined,
        loading: !settled,
    };
}
