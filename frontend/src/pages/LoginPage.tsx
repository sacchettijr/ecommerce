import type { FormEvent } from "react";
import { Link, Navigate } from "react-router";

import { login } from "../api/auth.ts";
import { withNext } from "../auth/authRoutes.ts";
import { useNext } from "../auth/useNext.ts";
import { AuthLayout } from "../components/auth/AuthLayout.tsx";
import { ResendConfirmation } from "../components/auth/ResendConfirmation.tsx";
import { SubmitButton } from "../components/ui/SubmitButton.tsx";
import { TextField } from "../components/ui/TextField.tsx";
import { textLinkClassName } from "../components/ui/linkClassNames.ts";
import { useAuth } from "../context/useAuth.ts";
import { useApiForm } from "../hooks/useApiForm.ts";
import { useLanguage } from "../i18n/useLanguage.ts";

export function LoginPage() {
    const { t } = useLanguage();
    const next = useNext();
    const { user, setUser } = useAuth();
    const form = useApiForm({ email: "", password: "" });

    // Já autenticado: segue direto para o destino (equivalente ao redirect_authenticated_user).
    if (user) {
        return <Navigate to={next || "/"} replace />;
    }

    const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        await form.submit(async () => {
            const authenticated = await login(
                form.values.email,
                form.values.password,
            );
            // O redirecionamento para o `next` acontece ao renderizar com o usuário definido.
            setUser(authenticated);
        });
    };

    return (
        <AuthLayout
            title={t.auth.login.title}
            heading={t.auth.login.heading}
            errors={form.generalErrors}
            errorActions={
                form.code === "email_not_verified" && (
                    <ResendConfirmation email={form.values.email} next={next} />
                )
            }
            links={
                <div className="flex justify-between">
                    <Link
                        to={withNext("/signup", next)}
                        className={textLinkClassName}
                    >
                        {t.auth.login.createAccount}
                    </Link>
                    <Link
                        to={withNext("/password-reset", next)}
                        className={textLinkClassName}
                    >
                        {t.auth.login.forgotPassword}
                    </Link>
                </div>
            }
        >
            <form onSubmit={onSubmit}>
                <TextField
                    name="email"
                    type="email"
                    label={t.auth.emailLabel}
                    autoComplete="email"
                    required
                    value={form.values.email}
                    onChange={form.onChange}
                    error={form.fieldErrors.email}
                />
                <TextField
                    name="password"
                    type="password"
                    label={t.auth.passwordLabel}
                    autoComplete="current-password"
                    required
                    value={form.values.password}
                    onChange={form.onChange}
                    error={form.fieldErrors.password}
                />
                <SubmitButton
                    submitting={form.submitting}
                    label={t.auth.login.submit}
                    submittingLabel={t.auth.login.submitting}
                />
            </form>
        </AuthLayout>
    );
}
