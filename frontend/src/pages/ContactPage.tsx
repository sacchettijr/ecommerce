import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";

import { ApiError } from "../api/client.ts";
import { sendContact } from "../api/contact.ts";
import type { ContactPayload } from "../api/types.ts";
import { FormField } from "../components/ui/FormField.tsx";
import { inputClassName } from "../components/ui/inputClassName.ts";
import {
    EnvelopeIcon,
    MapPinIcon,
    PhoneIcon,
    WhatsAppIcon,
} from "../components/ui/icons.tsx";
import { company } from "../config/company.ts";
import { useLanguage } from "../i18n/useLanguage.ts";
import type { Translations } from "../i18n/types.ts";

type Field = keyof ContactPayload;
type FieldErrors = Partial<Record<Field, string>>;
type Status = "idle" | "sending" | "success";

const fields: Field[] = ["name", "email", "phone", "message"];

const initialValues: ContactPayload = {
    name: "",
    email: "",
    phone: "",
    message: "",
};

function validate(
    values: ContactPayload,
    t: Translations["contact"],
): FieldErrors {
    const errors: FieldErrors = {};

    if (values.name.trim().length < 3) {
        errors.name = t.nameError;
    }
    if (!/^\S+@\S+\.\S+$/.test(values.email.trim())) {
        errors.email = t.emailError;
    }
    if (values.phone.replace(/\D/g, "").length < 10) {
        errors.phone = t.phoneError;
    }
    if (values.message.trim().length < 10) {
        errors.message = t.messageError;
    }

    return errors;
}

function serverErrors(data: unknown): FieldErrors {
    const errors: FieldErrors = {};

    if (typeof data !== "object" || data === null) {
        return errors;
    }

    const record = data as Record<string, unknown>;

    for (const field of fields) {
        const value = record[field];
        const message = Array.isArray(value) ? value[0] : value;

        if (typeof message === "string") {
            errors[field] = message;
        }
    }

    return errors;
}

export function ContactPage() {
    const { t } = useLanguage();
    const [values, setValues] = useState<ContactPayload>(initialValues);
    const [errors, setErrors] = useState<FieldErrors>({});
    const [formError, setFormError] = useState<string | null>(null);
    const [status, setStatus] = useState<Status>("idle");

    const onChange = (
        event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
    ) => {
        const { name, value } = event.target;
        setValues((current) => ({ ...current, [name]: value }));
    };

    const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const clientErrors = validate(values, t.contact);
        setErrors(clientErrors);
        setFormError(null);

        if (Object.keys(clientErrors).length > 0) {
            setStatus("idle");
            return;
        }

        setStatus("sending");

        try {
            await sendContact(values);
            setValues(initialValues);
            setStatus("success");
        } catch (error) {
            setStatus("idle");

            if (error instanceof ApiError && error.status === 400) {
                setErrors(serverErrors(error.data));
            } else if (error instanceof ApiError && error.status === 429) {
                setFormError(t.contact.rateLimitError);
            } else {
                setFormError(t.contact.genericError);
            }
        }
    };

    return (
        <>
            <title>{t.contact.title}</title>

            <div className="mx-auto max-w-7xl px-4 py-12">
                <h1 className="mb-6 text-3xl font-bold">{t.contact.heading}</h1>

                <div className="grid gap-10 lg:grid-cols-5">
                    <div className="lg:col-span-3">
                        {status === "success" && (
                            <div
                                role="status"
                                className="mb-4 rounded-lg bg-green-50 p-4 text-green-800 ring-1 ring-green-200"
                            >
                                {t.contact.success}
                            </div>
                        )}
                        {formError && (
                            <div
                                role="alert"
                                className="mb-4 rounded-lg bg-red-50 p-4 text-red-800 ring-1 ring-red-200"
                            >
                                {formError}
                            </div>
                        )}

                        <form onSubmit={onSubmit} noValidate>
                            <FormField
                                id="name"
                                label={t.contact.nameLabel}
                                required
                                error={errors.name}
                            >
                                <input
                                    id="name"
                                    name="name"
                                    type="text"
                                    autoComplete="name"
                                    value={values.name}
                                    onChange={onChange}
                                    aria-invalid={errors.name !== undefined}
                                    aria-describedby={
                                        errors.name ? "name-error" : undefined
                                    }
                                    className={inputClassName(
                                        errors.name !== undefined,
                                    )}
                                />
                            </FormField>

                            <FormField
                                id="email"
                                label={t.contact.emailLabel}
                                required
                                error={errors.email}
                            >
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    autoComplete="email"
                                    value={values.email}
                                    onChange={onChange}
                                    aria-invalid={errors.email !== undefined}
                                    aria-describedby={
                                        errors.email ? "email-error" : undefined
                                    }
                                    className={inputClassName(
                                        errors.email !== undefined,
                                    )}
                                />
                            </FormField>

                            <FormField
                                id="phone"
                                label={t.contact.phoneLabel}
                                required
                                error={errors.phone}
                            >
                                <input
                                    id="phone"
                                    name="phone"
                                    type="tel"
                                    autoComplete="tel"
                                    placeholder={t.contact.phonePlaceholder}
                                    value={values.phone}
                                    onChange={onChange}
                                    aria-invalid={errors.phone !== undefined}
                                    aria-describedby={
                                        errors.phone ? "phone-error" : undefined
                                    }
                                    className={inputClassName(
                                        errors.phone !== undefined,
                                    )}
                                />
                            </FormField>

                            <FormField
                                id="message"
                                label={t.contact.messageLabel}
                                required
                                error={errors.message}
                            >
                                <textarea
                                    id="message"
                                    name="message"
                                    rows={5}
                                    value={values.message}
                                    onChange={onChange}
                                    aria-invalid={errors.message !== undefined}
                                    aria-describedby={
                                        errors.message
                                            ? "message-error"
                                            : undefined
                                    }
                                    className={inputClassName(
                                        errors.message !== undefined,
                                    )}
                                />
                            </FormField>

                            <button
                                type="submit"
                                disabled={status === "sending"}
                                className="rounded-lg bg-blue-600 px-6 py-2.5 font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                {status === "sending"
                                    ? t.contact.sending
                                    : t.contact.send}
                            </button>
                        </form>
                    </div>

                    <aside className="lg:col-span-2">
                        <h2 className="mb-4 text-xl font-semibold">
                            {t.contact.otherContacts}
                        </h2>
                        <ul className="space-y-4">
                            <li className="flex gap-3">
                                <MapPinIcon className="mt-0.5 size-5 shrink-0 text-blue-600" />
                                <span>
                                    {company.addressLine1}
                                    <br />
                                    {company.addressLine2}
                                    <br />
                                    {company.addressCep}
                                </span>
                            </li>
                            <li className="flex gap-3">
                                <PhoneIcon className="mt-0.5 size-5 shrink-0 text-blue-600" />
                                <span>
                                    <a
                                        href={company.phoneHref}
                                        className="hover:underline"
                                    >
                                        {company.phone}
                                    </a>
                                    <a
                                        href={company.whatsappHref}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        title={t.footer.whatsapp}
                                        className="ml-3 inline-flex items-center gap-1 text-green-700 hover:underline"
                                    >
                                        <WhatsAppIcon className="size-4" />
                                        {t.footer.whatsapp}
                                    </a>
                                </span>
                            </li>
                            <li className="flex gap-3">
                                <EnvelopeIcon className="mt-0.5 size-5 shrink-0 text-blue-600" />
                                <a
                                    href={`mailto:${company.email}`}
                                    className="hover:underline"
                                >
                                    {company.email}
                                </a>
                            </li>
                        </ul>
                    </aside>
                </div>
            </div>
        </>
    );
}
