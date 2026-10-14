import type { FormEvent } from "react";
import { useEffect, useRef } from "react";
import { useNavigate } from "react-router";

import { updateProfile } from "../api/auth.ts";
import { AccountLayout } from "../components/account/AccountLayout.tsx";
import { Alert } from "../components/ui/Alert.tsx";
import { SubmitButton } from "../components/ui/SubmitButton.tsx";
import { TextField } from "../components/ui/TextField.tsx";
import { textLinkClassName } from "../components/ui/linkClassNames.ts";
import { useAuth } from "../context/useAuth.ts";
import { useApiForm } from "../hooks/useApiForm.ts";
import { useMessages } from "../hooks/useMessages.ts";
import { useLanguage } from "../i18n/useLanguage.ts";

export function ProfileEditPage() {
    const { t } = useLanguage();
    const navigate = useNavigate();
    const { user, loading, setUser } = useAuth();
    // ProtectedRoute only renders this page once a user is confirmed, so these values are
    // real on first render — the fallbacks only matter for the hook call itself.
    const form = useApiForm({
        name: user?.name ?? "",
        date_birth: user?.date_birth ?? "",
        phone: user?.phone ?? "",
    });
    const { messages, beginAction, replaceMessages, dismissMessage } =
        useMessages();
    const actionRef = useRef(0);

    useEffect(() => {
        if (form.generalErrors.length > 0) {
            replaceMessages(
                actionRef.current,
                form.generalErrors.map((text) => ({
                    variant: "error" as const,
                    text,
                })),
            );
        }
    }, [form.generalErrors, replaceMessages]);

    if (loading) {
        return (
            <AccountLayout title={t.profileEdit.title}>
                <p>{t.common.loading}</p>
            </AccountLayout>
        );
    }

    if (!user) {
        return (
            <AccountLayout title={t.profileEdit.title}>
                <Alert variant="error">{t.profile.loadError}</Alert>
            </AccountLayout>
        );
    }

    const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        actionRef.current = beginAction();

        const updated = await form.submit(async () => {
            const freshUser = await updateProfile(form.values);
            setUser(freshUser);
            form.setValues({
                name: freshUser.name,
                date_birth: freshUser.date_birth,
                phone: freshUser.phone,
            });
        });

        if (updated) {
            replaceMessages(actionRef.current, [
                { variant: "success", text: t.profileEdit.success },
            ]);
        }
    };

    return (
        <AccountLayout
            title={t.profileEdit.title}
            messages={messages}
            onDismissMessage={dismissMessage}
        >
            <h1 className="mb-6 text-2xl font-bold text-gray-900">
                {t.profileEdit.heading}
            </h1>

            <div className="rounded-lg bg-white p-6 shadow-sm ring-1 ring-gray-200">
                <form onSubmit={onSubmit} noValidate>
                    <TextField
                        name="name"
                        label={t.auth.nameLabel}
                        autoComplete="name"
                        required
                        value={form.values.name}
                        onChange={form.onChange}
                        error={form.fieldErrors.name}
                    />
                    <TextField
                        name="date_birth"
                        type="date"
                        label={t.auth.dateBirthLabel}
                        autoComplete="bday"
                        required
                        value={form.values.date_birth}
                        onChange={form.onChange}
                        error={form.fieldErrors.date_birth}
                    />
                    <TextField
                        name="phone"
                        type="tel"
                        label={t.auth.phoneLabel}
                        autoComplete="tel"
                        placeholder={t.auth.phonePlaceholder}
                        value={form.values.phone}
                        onChange={form.onChange}
                        error={form.fieldErrors.phone}
                    />

                    <div className="flex items-center gap-4">
                        <SubmitButton
                            submitting={form.submitting}
                            label={t.profileEdit.submit}
                            submittingLabel={t.profileEdit.submitting}
                        />
                        <button
                            type="button"
                            onClick={() => void navigate("/profile")}
                            className={textLinkClassName}
                        >
                            {t.profileEdit.cancel}
                        </button>
                    </div>
                </form>
            </div>
        </AccountLayout>
    );
}
