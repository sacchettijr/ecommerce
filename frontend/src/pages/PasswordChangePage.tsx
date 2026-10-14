import type { FormEvent } from "react";
import { useEffect, useRef } from "react";
import { useNavigate } from "react-router";

import { changePassword } from "../api/auth.ts";
import { AccountLayout } from "../components/account/AccountLayout.tsx";
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
    const { messages, beginAction, replaceMessages, dismissMessage } =
        useMessages();
    const actionRef = useRef(0);

    // Routes useApiForm's own general-error state (the backend's "same password" code, or any
    // other general/network error) into the shared notification area once it settles — reading
    // it here, reactively, instead of right after awaiting form.submit() below, is what makes
    // the token in actionRef.current reliably up to date for the action it belongs to.
    useEffect(() => {
        if (form.code === "password_unchanged") {
            replaceMessages(actionRef.current, [
                { variant: "warning", text: t.passwordChange.unchangedWarning },
            ]);
        } else if (form.generalErrors.length > 0) {
            replaceMessages(
                actionRef.current,
                form.generalErrors.map((text) => ({
                    variant: "error" as const,
                    text,
                })),
            );
        }
    }, [form.code, form.generalErrors, replaceMessages, t]);

    const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        actionRef.current = beginAction();

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
            replaceMessages(actionRef.current, [
                { variant: "success", text: t.passwordChange.success },
            ]);
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
