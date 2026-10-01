import { Link } from "react-router";

import { withNext } from "../auth/authRoutes.ts";
import { useNext } from "../auth/useNext.ts";
import { AuthLayout } from "../components/auth/AuthLayout.tsx";
import { buttonLinkClassName } from "../components/ui/linkClassNames.ts";
import { useLanguage } from "../i18n/useLanguage.ts";

export function PasswordResetCompletePage() {
    const { t } = useLanguage();
    const next = useNext();

    return (
        <AuthLayout
            title={t.auth.passwordResetConfirm.completeTitle}
            heading={t.auth.passwordResetConfirm.completeTitle}
            notice={t.auth.passwordResetConfirm.completeText}
            centered
            links={
                <Link
                    to={withNext("/login", next)}
                    className={buttonLinkClassName}
                >
                    {t.auth.passwordResetConfirm.goToLogin}
                </Link>
            }
        />
    );
}
