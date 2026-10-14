import type { ReactElement } from "react";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router";

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
}

export function renderWithProviders(
    ui: ReactElement,
    { user = null, loading = false, route = "/" }: RenderOptions = {},
) {
    const authValue: AuthState = { user, loading, setUser: () => {} };

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
                <AuthContext value={authValue}>{ui}</AuthContext>
            </LanguageContext>
        </MemoryRouter>,
    );
}
