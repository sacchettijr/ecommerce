import type { FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router";

import {
    confirmPasswordReset,
    validatePasswordResetLink,
} from "../api/auth.ts";
import { ApiError } from "../api/client.ts";
import { withNext } from "../auth/authRoutes.ts";
import { useNext } from "../auth/useNext.ts";
import { AuthLayout } from "../components/auth/AuthLayout.tsx";
import { SubmitButton } from "../components/ui/SubmitButton.tsx";
import { TextField } from "../components/ui/TextField.tsx";
import { buttonLinkClassName } from "../components/ui/linkClassNames.ts";
import { useApiForm } from "../hooks/useApiForm.ts";
import { useAsync } from "../hooks/useAsync.ts";
import { useLanguage } from "../i18n/useLanguage.ts";
import { NotFoundPage } from "./NotFoundPage.tsx";

function ResetForm({ uid, token }: { uid: string; token: string }) {
    const { t } = useLanguage();
    const next = useNext();
    const navigate = useNavigate();
    const form = useApiForm({ new_password1: "", new_password2: "" });

    const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const changed = await form.submit(() =>
            confirmPasswordReset(
                uid,
                token,
                form.values.new_password1,
                form.values.new_password2,
            ),
        );

        if (changed) {
            void navigate(withNext("/password-reset/complete", next));
        }
    };

    return (
        <AuthLayout
            title={t.auth.passwordResetConfirm.title}
            heading={t.auth.passwordResetConfirm.heading}
            errors={form.generalErrors}
        >
            <form onSubmit={onSubmit}>
                <TextField
                    name="new_password1"
                    type="password"
                    label={t.auth.newPasswordLabel}
                    autoComplete="new-password"
                    required
                    value={form.values.new_password1}
                    onChange={form.onChange}
                    error={form.fieldErrors.new_password1}
                />
                <TextField
                    name="new_password2"
                    type="password"
                    label={t.auth.confirmNewPasswordLabel}
                    autoComplete="new-password"
                    required
                    value={form.values.new_password2}
                    onChange={form.onChange}
                    error={form.fieldErrors.new_password2}
                />
                <SubmitButton
                    submitting={form.submitting}
                    label={t.auth.passwordResetConfirm.submit}
                    submittingLabel={t.auth.passwordResetConfirm.submitting}
                />
            </form>
        </AuthLayout>
    );
}

// O token só é validado pelo Django; a chave "uid/token" é um valor primitivo para o useAsync.
function validateLink(key: string, signal: AbortSignal): Promise<void> {
    const [uid = "", token = ""] = key.split("/");

    return validatePasswordResetLink(uid, token, signal);
}

function ResetConfirm({ uid, token }: { uid: string; token: string }) {
    const { t } = useLanguage();
    const next = useNext();
    const { error, loading } = useAsync(validateLink, `${uid}/${token}`);

    if (loading) {
        return (
            <AuthLayout
                title={t.auth.passwordResetConfirm.title}
                heading={t.auth.passwordResetConfirm.checking}
            />
        );
    }

    if (error instanceof ApiError && error.status === 400) {
        return (
            <AuthLayout
                title={t.auth.passwordResetConfirm.invalidTitle}
                heading={t.auth.passwordResetConfirm.invalidTitle}
                intro={t.auth.passwordResetConfirm.invalidText}
                centered
            >
                <div className="text-center">
                    <Link
                        to={withNext("/password-reset", next)}
                        className={buttonLinkClassName}
                    >
                        {t.auth.passwordResetConfirm.requestNew}
                    </Link>
                </div>
            </AuthLayout>
        );
    }

    if (error !== undefined) {
        return (
            <AuthLayout
                title={t.auth.passwordResetConfirm.title}
                heading={t.auth.passwordResetConfirm.heading}
                errors={[
                    error instanceof ApiError
                        ? t.auth.errors.generic
                        : t.auth.errors.network,
                ]}
            />
        );
    }

    return <ResetForm uid={uid} token={token} />;
}

export function PasswordResetConfirmPage() {
    const { uid, token } = useParams<{ uid: string; token: string }>();

    if (uid === undefined || token === undefined) {
        return <NotFoundPage />;
    }

    return <ResetConfirm key={`${uid}/${token}`} uid={uid} token={token} />;
}
