import { Link } from "react-router";

import { withNext } from "../auth/authRoutes.ts";
import { useNext } from "../auth/useNext.ts";
import { AuthLayout } from "../components/auth/AuthLayout.tsx";
import { textLinkClassName } from "../components/ui/linkClassNames.ts";
import { useLanguage } from "../i18n/useLanguage.ts";

export function PasswordResetDonePage() {
    const { t } = useLanguage();
    const next = useNext();

    return (
        <AuthLayout
            title={t.auth.passwordReset.doneTitle}
            heading={t.auth.passwordReset.doneTitle}
            notice={t.auth.passwordReset.doneText}
            centered
            links={
                <Link
                    to={withNext("/login", next)}
                    className={textLinkClassName}
                >
                    {t.auth.passwordReset.backToLogin}
                </Link>
            }
        />
    );
}
