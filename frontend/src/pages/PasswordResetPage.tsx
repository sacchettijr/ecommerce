import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router";

import { requestPasswordReset } from "../api/auth.ts";
import { withNext } from "../auth/authRoutes.ts";
import { useNext } from "../auth/useNext.ts";
import { AuthLayout } from "../components/auth/AuthLayout.tsx";
import { SubmitButton } from "../components/ui/SubmitButton.tsx";
import { TextField } from "../components/ui/TextField.tsx";
import { textLinkClassName } from "../components/ui/linkClassNames.ts";
import { useApiForm } from "../hooks/useApiForm.ts";
import { useLanguage } from "../i18n/useLanguage.ts";

export function PasswordResetPage() {
    const { t } = useLanguage();
    const next = useNext();
    const navigate = useNavigate();
    const form = useApiForm({ email: "" });

    const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const requested = await form.submit(() =>
            requestPasswordReset(form.values.email, next),
        );

        if (requested) {
            void navigate(withNext("/password-reset/done", next));
        }
    };

    return (
        <AuthLayout
            title={t.auth.passwordReset.title}
            heading={t.auth.passwordReset.heading}
            intro={t.auth.passwordReset.intro}
            errors={form.generalErrors}
            links={
                <Link
                    to={withNext("/login", next)}
                    className={textLinkClassName}
                >
                    {t.auth.passwordReset.backToLogin}
                </Link>
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
                <SubmitButton
                    submitting={form.submitting}
                    label={t.auth.passwordReset.submit}
                    submittingLabel={t.auth.passwordReset.submitting}
                />
            </form>
        </AuthLayout>
    );
}
