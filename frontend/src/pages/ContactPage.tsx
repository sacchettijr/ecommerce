import { useEffect, useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import { isValidPhoneNumber } from "libphonenumber-js/min";

import { ApiError } from "../api/client.ts";
import { sendContact } from "../api/contact.ts";
import type { ContactPayload } from "../api/types.ts";
import { FormField } from "../components/ui/FormField.tsx";
import { PhoneInput } from "../components/ui/PhoneInput.tsx";
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
const COOLDOWN_STORAGE_KEY = "contact_cooldown_until";

const initialValues: ContactPayload = {
    name: "",
    email: "",
    phone: "",
    message: "",
};

// Mirrors the backend's validate_name (utils/validator.py): at least two
// whitespace-separated parts that each contain a letter — a single word isn't a full name.
function hasFullName(value: string): boolean {
    const parts = value
        .trim()
        .split(/\s+/)
        .filter((part) => /\p{L}/u.test(part));

    return parts.length >= 2;
}

function validate(
    values: ContactPayload,
    t: Translations["contact"],
): FieldErrors {
    const errors: FieldErrors = {};

    if (!hasFullName(values.name)) {
        errors.name = t.nameError;
    }
    if (!/^\S+@\S+\.\S+$/.test(values.email.trim())) {
        errors.email = t.emailError;
    }
    if (!isValidPhoneNumber(values.phone)) {
        errors.phone = t.phoneError;
    }
    if (values.message.trim().length < 10) {
        errors.message = t.messageError;
    }

    return errors;
}

function readStoredCooldownSeconds(): number {
    try {
        const until = Number(localStorage.getItem(COOLDOWN_STORAGE_KEY));
        const remaining = Math.ceil((until - Date.now()) / 1000);
        return remaining > 0 ? remaining : 0;
    } catch {
        return 0;
    }
}

function storeCooldownUntil(seconds: number): void {
    try {
        localStorage.setItem(
            COOLDOWN_STORAGE_KEY,
            String(Date.now() + seconds * 1000),
        );
    } catch {
        // No persistence available (private mode, storage disabled, ...) — the countdown
        // still works for this page load via in-memory state; it just won't survive a
        // reload. The backend remains the real enforcement point regardless.
    }
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
    // Seconds left in an active cooldown, or 0 when none is active. Seeded from
    // localStorage on mount so a reload doesn't presume a prior block already ended —
    // the backend is re-checked for real on the next actual submit attempt regardless.
    const [cooldownSeconds, setCooldownSeconds] = useState(
        readStoredCooldownSeconds,
    );

    useEffect(() => {
        if (cooldownSeconds <= 0) {
            return;
        }

        const interval = setInterval(() => {
            setCooldownSeconds((current) => Math.max(0, current - 1));
        }, 1000);

        return () => clearInterval(interval);
    }, [cooldownSeconds]);

    const onChange = (
        event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
    ) => {
        const { name, value } = event.target;
        setValues((current) => ({ ...current, [name]: value }));
    };

    const onPhoneChange = (phone: string) => {
        setValues((current) => ({ ...current, phone }));
    };

    const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        if (cooldownSeconds > 0) {
            return;
        }

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
                const retryAfter = (error.data as { retry_after?: unknown } | null)
                    ?.retry_after;

                if (typeof retryAfter === "number" && retryAfter > 0) {
                    storeCooldownUntil(retryAfter);
                    setCooldownSeconds(retryAfter);
                } else {
                    setFormError(t.contact.rateLimitError);
                }
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
                        {cooldownSeconds > 0 && (
                            <div
                                role="alert"
                                aria-live="polite"
                                className="mb-4 rounded-lg bg-red-50 p-4 text-red-800 ring-1 ring-red-200"
                            >
                                {t.contact.rateLimitCountdown(cooldownSeconds)}
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

                            <PhoneInput
                                id="phone"
                                label={t.contact.phoneLabel}
                                countrySelectLabel={t.contact.phoneCountryLabel}
                                required
                                value={values.phone}
                                onChange={onPhoneChange}
                                error={errors.phone}
                            />

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
                                disabled={status === "sending" || cooldownSeconds > 0}
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
