import type { ReactElement } from "react";
import { render } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router";

import { AuthContext } from "../context/AuthContext.ts";
import type { AuthState } from "../context/AuthContext.ts";
import { CartContext } from "../context/CartContext.ts";
import type { CartState } from "../context/CartContext.ts";
import type { CartSummary, SessionUser } from "../api/types.ts";
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
    }: RenderOptions = {},
) {
    const authValue: AuthState = { user, loading, setUser };
    const cartValue: CartState = { cart, loading: cartLoading, error: cartError, setCart };

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
                        {path ? (
                            <Routes>
                                <Route path={path} element={ui} />
                            </Routes>
                        ) : (
                            ui
                        )}
                    </CartContext>
                </AuthContext>
            </LanguageContext>
        </MemoryRouter>,
    );
}
