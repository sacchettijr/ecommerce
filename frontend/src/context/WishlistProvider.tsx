import { useCallback, useState } from "react";
import type { ReactNode } from "react";

import { fetchMyWishlist } from "../api/wishlist.ts";
import type { WishlistItem } from "../api/types.ts";
import { useAsync } from "../hooks/useAsync.ts";
import { useAuth } from "./useAuth.ts";
import { WishlistContext } from "./WishlistContext.ts";

export function WishlistProvider({ children }: { children: ReactNode }) {
    const { user } = useAuth();
    const userId = user?.id ?? null;

    // Every wishlist endpoint requires authentication — skip the request entirely while
    // logged out instead of letting it 403. useAsync re-runs this whenever `userId`
    // changes (login, logout, or switching accounts), which is exactly when the wishlist
    // should be re-fetched. Mirrors CartProvider.tsx's exact shape.
    const fetchForUser = useCallback(
        (id: number | null, signal: AbortSignal): Promise<WishlistItem[]> =>
            id === null ? Promise.resolve([]) : fetchMyWishlist(undefined, signal),
        [],
    );

    const { data, error, loading } = useAsync(fetchForUser, userId);
    // Depois de uma mutação (add/remove) a resposta dela vale mais que o último fetch —
    // mesmo padrão do AuthProvider/CartProvider.
    const [override, setOverride] = useState<WishlistItem[] | null>(null);

    // Reseta durante a renderização (não num efeito, para não disparar uma renderização
    // em cascata) sempre que a conta muda, para um override da conta anterior nunca
    // "vazar" para a próxima.
    const [lastUserId, setLastUserId] = useState(userId);
    if (userId !== lastUserId) {
        setLastUserId(userId);
        setOverride(null);
    }

    const items = override ?? data ?? null;

    return (
        <WishlistContext
            value={{
                items,
                loading: loading && override === null,
                error: error !== undefined && override === null,
                setItems: setOverride,
            }}
        >
            {children}
        </WishlistContext>
    );
}
