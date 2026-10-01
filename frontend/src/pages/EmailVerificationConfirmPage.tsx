import { Link, useParams } from "react-router";

import { confirmEmail } from "../api/auth.ts";
import { ApiError } from "../api/client.ts";
import { withNext } from "../auth/authRoutes.ts";
import { useNext } from "../auth/useNext.ts";
import { AuthLayout } from "../components/auth/AuthLayout.tsx";
import { buttonLinkClassName } from "../components/ui/linkClassNames.ts";
import { useAsync } from "../hooks/useAsync.ts";
import { useLanguage } from "../i18n/useLanguage.ts";
import { NotFoundPage } from "./NotFoundPage.tsx";

// O link é de uso único: o token deixa de valer assim que o e-mail é confirmado. Como o
// React (StrictMode, remontagens) pode montar a página duas vezes, a mesma chamada é
// reaproveitada em vez de enviar a confirmação uma segunda vez e mostrar "inválido".
const attempts = new Map<string, Promise<void>>();

function confirmOnce(key: string): Promise<void> {
    const existing = attempts.get(key);

    if (existing) {
        return existing;
    }

    const [uid = "", token = ""] = key.split("/");
    const attempt = confirmEmail(uid, token);

    attempts.set(key, attempt);
    // Falha de rede: permite tentar de novo. Resposta da API (inclusive link inválido) é definitiva.
    attempt.catch((error: unknown) => {
        if (!(error instanceof ApiError)) {
            attempts.delete(key);
        }
    });

    return attempt;
}

function EmailVerification({ uid, token }: { uid: string; token: string }) {
    const { t } = useLanguage();
    const next = useNext();
    const { error, loading } = useAsync(confirmOnce, `${uid}/${token}`);

    if (loading) {
        return (
            <AuthLayout
                title={t.auth.emailVerification.title}
                heading={t.auth.emailVerification.checking}
                centered
            />
        );
    }

    if (error === undefined) {
        return (
            <AuthLayout
                title={t.auth.emailVerification.title}
                heading={t.auth.emailVerification.successTitle}
                notice={t.auth.emailVerification.successText}
                centered
                links={
                    <Link
                        to={withNext("/login", next)}
                        className={buttonLinkClassName}
                    >
                        {t.auth.emailVerification.login}
                    </Link>
                }
            />
        );
    }

    if (error instanceof ApiError && error.status === 400) {
        return (
            <AuthLayout
                title={t.auth.emailVerification.title}
                heading={t.auth.emailVerification.invalidTitle}
                intro={t.auth.emailVerification.invalidText}
                centered
                links={
                    <Link
                        to={withNext("/login", next)}
                        className={buttonLinkClassName}
                    >
                        {t.auth.emailVerification.backToLogin}
                    </Link>
                }
            />
        );
    }

    return (
        <AuthLayout
            title={t.auth.emailVerification.title}
            heading={t.auth.emailVerification.title}
            errors={[
                error instanceof ApiError
                    ? t.auth.errors.generic
                    : t.auth.errors.network,
            ]}
        />
    );
}

export function EmailVerificationConfirmPage() {
    const { uid, token } = useParams<{ uid: string; token: string }>();

    if (uid === undefined || token === undefined) {
        return <NotFoundPage />;
    }

    return (
        <EmailVerification key={`${uid}/${token}`} uid={uid} token={token} />
    );
}
