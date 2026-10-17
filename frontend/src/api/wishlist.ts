import { apiDelete, apiGet, apiPost } from "./client.ts";
import type { PublicWishlist, WishlistItem } from "./types.ts";

// Always scoped to the authenticated session on the backend — no user id is ever sent here.
export function fetchMyWishlist(
    _arg: undefined,
    signal: AbortSignal,
): Promise<WishlistItem[]> {
    return apiGet<WishlistItem[]>("/account/wishlist/", signal);
}

// Returns the requesting user's full, authoritative item list (not just the new one),
// same convention as setPrimaryAddress.
export function addToWishlist(
    productId: number,
    signal?: AbortSignal,
): Promise<WishlistItem[]> {
    return apiPost<WishlistItem[]>(
        "/account/wishlist/",
        { product: productId },
        signal,
    );
}

export function removeFromWishlistItem(
    itemId: number,
    signal?: AbortSignal,
): Promise<WishlistItem[]> {
    return apiDelete<WishlistItem[]>(`/account/wishlist/${itemId}/`, signal);
}

export function toggleWishlistItemPrivacy(
    itemId: number,
    signal?: AbortSignal,
): Promise<WishlistItem[]> {
    return apiPost<WishlistItem[]>(
        `/account/wishlist/${itemId}/toggle-privacy/`,
        {},
        signal,
    );
}

export function moveWishlistItem(
    itemId: number,
    direction: "up" | "down",
    signal?: AbortSignal,
): Promise<WishlistItem[]> {
    return apiPost<WishlistItem[]>(
        `/account/wishlist/${itemId}/move/`,
        { direction },
        signal,
    );
}

export function checkWishlistMembership(
    productId: number,
    signal?: AbortSignal,
): Promise<{ in_wishlist: boolean; item_id: number | null }> {
    return apiGet<{ in_wishlist: boolean; item_id: number | null }>(
        `/account/wishlist/check/?product=${productId}`,
        signal,
    );
}

export function fetchWishlistShareLink(
    signal?: AbortSignal,
): Promise<{ public_id: string }> {
    return apiGet<{ public_id: string }>("/account/wishlist/share-link/", signal);
}

export function fetchPublicWishlist(
    publicId: string,
    signal?: AbortSignal,
): Promise<PublicWishlist> {
    return apiGet<PublicWishlist>(
        `/account/wishlist/public/${publicId}/`,
        signal,
    );
}
