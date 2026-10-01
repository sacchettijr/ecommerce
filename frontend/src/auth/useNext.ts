import { useSearchParams } from "react-router";

import { safeNext } from "./safeNext.ts";

export function useNext(): string {
    const [searchParams] = useSearchParams();

    return safeNext(searchParams.get("next"));
}
