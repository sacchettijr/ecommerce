import type { FormEvent } from "react";
import { useNavigate } from "react-router";

import { changePassword } from "../api/auth.ts";
import { AccountLayout } from "../components/account/AccountLayout.tsx";
import { Alert } from "../components/ui/Alert.tsx";
import { SubmitButton } from "../components/ui/SubmitButton.tsx";
import { TextField } from "../components/ui/TextField.tsx";
import { textLinkClassName } from "../components/ui/linkClassNames.ts";
import { useApiForm } from "../hooks/useApiForm.ts";
import { useMessages } from "../hooks/useMessages.ts";
import { useLanguage } from "../i18n/useLanguage.ts";

const emptyValues = { old_password: "", new_password1: "", new_password2: "" };

export function PasswordChangePage() {
    const { t } = useLanguage();
    const navigate = useNavigate();
    const form = useApiForm(emptyValues);
    const { messages, addMessage, dismissMessage } = useMessages();

    const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const changed = await form.submit(() =>
            changePassword(
                form.values.old_password,
                form.values.new_password1,
                form.values.new_password2,
            ),
        );

        if (changed) {
            // Never keep a just-submitted password sitting in form state once it succeeded.
            form.setValues(emptyValues);
            addMessage("success", t.passwordChange.success);
        }
    };

    return (
        <AccountLayout
            title={t.passwordChange.title}
            messages={messages}
            onDismissMessage={dismissMessage}
        >
            <h1 className="mb-6 text-2xl font-bold text-gray-900">
                {t.passwordChange.heading}
            </h1>

            <div className="rounded-lg bg-white p-6 shadow-sm ring-1 ring-gray-200">
                {form.generalErrors.map((error) => (
                    <Alert key={error} variant="error">
                        {error}
                    </Alert>
                ))}

                <form onSubmit={onSubmit} noValidate>
                    <TextField
                        name="old_password"
                        type="password"
                        label={t.auth.currentPasswordLabel}
                        autoComplete="current-password"
                        required
                        value={form.values.old_password}
                        onChange={form.onChange}
                        error={form.fieldErrors.old_password}
                    />
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

                    <div className="flex items-center gap-4">
                        <SubmitButton
                            submitting={form.submitting}
                            label={t.passwordChange.submit}
                            submittingLabel={t.passwordChange.submitting}
                        />
                        <button
                            type="button"
                            onClick={() => void navigate("/profile")}
                            className={textLinkClassName}
                        >
                            {t.passwordChange.cancel}
                        </button>
                    </div>
                </form>
            </div>
        </AccountLayout>
    );
}
