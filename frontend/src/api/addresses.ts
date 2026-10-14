import { apiGet, apiPost } from "./client.ts";
import type { UserAddress } from "./types.ts";

// Always scoped to the authenticated session on the backend — no user id is ever sent here.
export function fetchUserAddresses(
    _arg: undefined,
    signal: AbortSignal,
): Promise<UserAddress[]> {
    return apiGet<UserAddress[]>("/account/addresses/", signal);
}

// Returns the requesting user's full, authoritative address list (not just the one address),
// since switching primary also changes the previous primary address's own state.
export function setPrimaryAddress(
    id: number,
    signal?: AbortSignal,
): Promise<UserAddress[]> {
    return apiPost<UserAddress[]>(
        `/account/addresses/${id}/set-primary/`,
        {},
        signal,
    );
}
