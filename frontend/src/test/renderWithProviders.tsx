import type { ReactElement } from "react";
import { render } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router";

import { AuthContext } from "../context/AuthContext.ts";
import type { AuthState } from "../context/AuthContext.ts";
import type { SessionUser } from "../api/types.ts";
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
}

export function renderWithProviders(
    ui: ReactElement,
    {
        user = null,
        loading = false,
        route = "/",
        path,
        setUser = () => {},
    }: RenderOptions = {},
) {
    const authValue: AuthState = { user, loading, setUser };

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
                    {path ? (
                        <Routes>
                            <Route path={path} element={ui} />
                        </Routes>
                    ) : (
                        ui
                    )}
                </AuthContext>
            </LanguageContext>
        </MemoryRouter>,
    );
}
