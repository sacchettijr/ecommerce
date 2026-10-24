import { apiDelete, apiGet, apiPatch, apiPost } from "./client.ts";
import type { CartSummary } from "./types.ts";

// Always scoped to the authenticated session on the backend — no user id is ever sent here.
export function fetchCart(_arg: undefined, signal: AbortSignal): Promise<CartSummary> {
    return apiGet<CartSummary>("/checkout/items/", signal);
}

export function addToCart(
    productId: number,
    quantity?: number,
    signal?: AbortSignal,
): Promise<CartSummary> {
    return apiPost<CartSummary>(
        "/checkout/items/",
        { product: productId, ...(quantity ? { quantity } : {}) },
        signal,
    );
}

export function updateCartItemQuantity(
    itemId: number,
    quantity: number,
    signal?: AbortSignal,
): Promise<CartSummary> {
    return apiPatch<CartSummary>(`/checkout/items/${itemId}/`, { quantity }, signal);
}

export function removeCartItem(itemId: number, signal?: AbortSignal): Promise<CartSummary> {
    return apiDelete<CartSummary>(`/checkout/items/${itemId}/`, signal);
}
