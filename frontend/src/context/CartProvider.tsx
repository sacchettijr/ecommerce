import { useCallback, useState } from "react";
import type { ReactNode } from "react";

import { fetchCart } from "../api/cart.ts";
import type { CartSummary } from "../api/types.ts";
import { useAsync } from "../hooks/useAsync.ts";
import { CartContext } from "./CartContext.ts";
import { useAuth } from "./useAuth.ts";

const EMPTY_CART: CartSummary = {
    items: [],
    subtotal: "0.00",
    discount_total: "0.00",
    total: "0.00",
};

export function CartProvider({ children }: { children: ReactNode }) {
    const { user } = useAuth();
    const userId = user?.id ?? null;

    // Every cart endpoint requires authentication — skip the request entirely while
    // logged out instead of letting it 403. useAsync re-runs this whenever `userId`
    // changes (login, logout, or switching accounts), which is exactly when the cart
    // should be re-fetched.
    const fetchForUser = useCallback(
        (id: number | null, signal: AbortSignal): Promise<CartSummary> =>
            id === null ? Promise.resolve(EMPTY_CART) : fetchCart(undefined, signal),
        [],
    );

    const { data, error, loading } = useAsync(fetchForUser, userId);
    // Depois de uma mutação (add/update/remove) a resposta dela vale mais que o último
    // fetch — mesmo padrão do AuthProvider.
    const [override, setOverride] = useState<CartSummary | null>(null);

    // Um override de uma conta anterior nunca deve "vazar" para a próxima conta que
    // logar (ou para o estado deslogado, após um logout). Reseta durante a renderização
    // (padrão recomendado pelo React para "ajustar estado quando uma prop muda"), não
    // num efeito, para não disparar uma renderização em cascata.
    const [lastUserId, setLastUserId] = useState(userId);
    if (userId !== lastUserId) {
        setLastUserId(userId);
        setOverride(null);
    }

    const cart = override ?? data ?? null;

    return (
        <CartContext
            value={{
                cart,
                loading: loading && override === null,
                error: error !== undefined && override === null,
                setCart: setOverride,
            }}
        >
            {children}
        </CartContext>
    );
}
