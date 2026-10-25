import type { ReactElement } from "react";
import { render } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router";

import { AuthContext } from "../context/AuthContext.ts";
import type { AuthState } from "../context/AuthContext.ts";
import { CartContext } from "../context/CartContext.ts";
import type { CartState } from "../context/CartContext.ts";
import { WishlistContext } from "../context/WishlistContext.ts";
import type { WishlistState } from "../context/WishlistContext.ts";
import type { CartSummary, SessionUser, WishlistItem } from "../api/types.ts";
import { LanguageContext } from "../i18n/LanguageContext.ts";
import { LANGUAGES } from "../i18n/languages.ts";
import { translations } from "../i18n/locales/index.ts";

interface RenderOptions {
    user?: SessionUser | null;
    loading?: boolean;
    route?: string;
    // A react-router path pattern (e.g. "product/:slug") to match `route` against — needed
    // only when `ui` itself calls useParams(); omit it to render `ui` directly, as before.
    path?: string;
    setUser?: (user: SessionUser | null) => void;
    cart?: CartSummary | null;
    cartLoading?: boolean;
    cartError?: boolean;
    setCart?: (cart: CartSummary) => void;
    wishlistItems?: WishlistItem[] | null;
    wishlistLoading?: boolean;
    wishlistError?: boolean;
    setWishlistItems?: (items: WishlistItem[]) => void;
}

export function renderWithProviders(
    ui: ReactElement,
    {
        user = null,
        loading = false,
        route = "/",
        path,
        setUser = () => {},
        cart = null,
        cartLoading = false,
        cartError = false,
        setCart = () => {},
        wishlistItems = null,
        wishlistLoading = false,
        wishlistError = false,
        setWishlistItems = () => {},
    }: RenderOptions = {},
) {
    const authValue: AuthState = { user, loading, setUser };
    const cartValue: CartState = { cart, loading: cartLoading, error: cartError, setCart };
    const wishlistValue: WishlistState = {
        items: wishlistItems,
        loading: wishlistLoading,
        error: wishlistError,
        setItems: setWishlistItems,
    };

    return render(
        <MemoryRouter initialEntries={[route]}>
            <LanguageContext
                value={{
                    language: "en",
                    setLanguage: () => {},
                    languages: LANGUAGES,
                    t: translations.en,
                }}
            >
                <AuthContext value={authValue}>
                    <CartContext value={cartValue}>
                        <WishlistContext value={wishlistValue}>
                            {path ? (
                                <Routes>
                                    <Route path={path} element={ui} />
                                </Routes>
                            ) : (
                                ui
                            )}
                        </WishlistContext>
                    </CartContext>
                </AuthContext>
            </LanguageContext>
        </MemoryRouter>,
    );
}
