import { Link } from "react-router";

import { AuthLayout } from "../components/auth/AuthLayout.tsx";
import { buttonLinkClassName } from "../components/ui/linkClassNames.ts";
import { useLanguage } from "../i18n/useLanguage.ts";

export function LoggedOutPage() {
    const { t } = useLanguage();

    return (
        <AuthLayout
            title={t.auth.loggedOut.title}
            heading={t.auth.loggedOut.heading}
            intro={t.auth.loggedOut.text}
            centered
            links={
                <Link to="/login" className={buttonLinkClassName}>
                    {t.auth.loggedOut.loginAgain}
                </Link>
            }
        />
    );
}
