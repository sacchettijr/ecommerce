import { useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router";

import { signup } from "../api/auth.ts";
import { withNext } from "../auth/authRoutes.ts";
import { useNext } from "../auth/useNext.ts";
import { AuthLayout } from "../components/auth/AuthLayout.tsx";
import { ResendConfirmation } from "../components/auth/ResendConfirmation.tsx";
import { SubmitButton } from "../components/ui/SubmitButton.tsx";
import { TextField } from "../components/ui/TextField.tsx";
import {
    buttonLinkClassName,
    textLinkClassName,
} from "../components/ui/linkClassNames.ts";
import { useApiForm } from "../hooks/useApiForm.ts";
import { useLanguage } from "../i18n/useLanguage.ts";

export function SignupPage() {
    const { t } = useLanguage();
    const next = useNext();
    const form = useApiForm({
        name: "",
        email: "",
        date_birth: "",
        phone: "",
        password1: "",
        password2: "",
    });
    // E-mail para o qual a confirmação foi enviada; definido só quando o cadastro deu certo.
    const [registeredEmail, setRegisteredEmail] = useState<string | null>(null);

    if (registeredEmail !== null) {
        return (
            <AuthLayout
                title={t.auth.signup.title}
                heading={t.auth.signup.successTitle}
                notice={t.auth.signup.successText(registeredEmail)}
                centered
            >
                <div className="text-center">
                    <ResendConfirmation email={registeredEmail} next={next} />
                    <Link
                        to={withNext("/login", next)}
                        className={`${buttonLinkClassName} mt-6`}
                    >
                        {t.auth.signup.goToLogin}
                    </Link>
                </div>
            </AuthLayout>
        );
    }

    const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const created = await form.submit(() => signup(form.values, next));

        if (created) {
            setRegisteredEmail(form.values.email);
        }
    };

    return (
        <AuthLayout
            title={t.auth.signup.title}
            heading={t.auth.signup.heading}
            errors={form.generalErrors}
            links={
                <Link
                    to={withNext("/login", next)}
                    className={textLinkClassName}
                >
                    {t.auth.signup.haveAccount}
                </Link>
            }
        >
            <form onSubmit={onSubmit}>
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
                <TextField
                    name="password1"
                    type="password"
                    label={t.auth.password1Label}
                    autoComplete="new-password"
                    required
                    value={form.values.password1}
                    onChange={form.onChange}
                    error={form.fieldErrors.password1}
                />
                <TextField
                    name="password2"
                    type="password"
                    label={t.auth.password2Label}
                    autoComplete="new-password"
                    required
                    value={form.values.password2}
                    onChange={form.onChange}
                    error={form.fieldErrors.password2}
                />
                <SubmitButton
                    submitting={form.submitting}
                    label={t.auth.signup.submit}
                    submittingLabel={t.auth.signup.submitting}
                />
            </form>
        </AuthLayout>
    );
}
