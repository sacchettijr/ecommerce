import { createContext } from "react";

import type { WishlistItem } from "../api/types.ts";

export interface WishlistState {
    items: WishlistItem[] | null;
    // true até a primeira resposta da wishlist (ou até ficarmos sabendo que o usuário
    // está deslogado, caso em que não há requisição alguma).
    loading: boolean;
    error: boolean;
    setItems: (items: WishlistItem[]) => void;
}

export const WishlistContext = createContext<WishlistState>({
    items: null,
    loading: true,
    error: false,
    setItems: () => {},
});
