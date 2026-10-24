import { createContext } from "react";

import type { CartSummary } from "../api/types.ts";

export interface CartState {
    cart: CartSummary | null;
    // true até a primeira resposta do carrinho (ou até ficarmos sabendo que o usuário
    // está deslogado, caso em que não há requisição alguma).
    loading: boolean;
    error: boolean;
    setCart: (cart: CartSummary) => void;
}

export const CartContext = createContext<CartState>({
    cart: null,
    loading: true,
    error: false,
    setCart: () => {},
});
