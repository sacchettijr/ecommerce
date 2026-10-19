import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import type { ChangeEvent, KeyboardEvent } from "react";
import {
    AsYouType,
    getCountryCallingCode,
    validatePhoneNumberLength,
} from "libphonenumber-js/min";
import type { CountryCode } from "libphonenumber-js/min";

import { Dropdown } from "./Dropdown.tsx";
import { FormField } from "./FormField.tsx";
import { inputClassName } from "./inputClassName.ts";
import { useLanguage } from "../../i18n/useLanguage.ts";

const DEFAULT_COUNTRY: CountryCode = "BR";

// The only countries this site currently serves — not the full ITU list.
const SUPPORTED_COUNTRIES = ["BR", "US", "FR", "IT"] as const satisfies readonly CountryCode[];

// Reuses the exact flag images the language switcher already ships
// (frontend/src/i18n/languages.ts) instead of a second flag asset/emoji — a native
// <select> can't render an <img> in its own collapsed display, which is why the country
// picker below is a Dropdown (like LanguagePicker) rather than a plain <select>.
const COUNTRY_FLAGS: Record<(typeof SUPPORTED_COUNTRIES)[number], string> = {
    BR: "/img/locale/pt-br.png",
    US: "/img/locale/en.png",
    FR: "/img/locale/fr.png",
    IT: "/img/locale/it.png",
};

// Representative national-number digits per supported country, chosen to produce a
// nicely grouped example once run through the same AsYouType formatter the real input
// uses — kept in sync with the actual mask automatically, rather than hand-typed format
// strings that could drift from it.
const PLACEHOLDER_DIGITS: Record<(typeof SUPPORTED_COUNTRIES)[number], string> = {
    BR: "69991234567",
    US: "2025551234",
    FR: "0612345678",
    IT: "3123456789",
};

function placeholderFor(country: CountryCode): string {
    const digits = PLACEHOLDER_DIGITS[country as (typeof SUPPORTED_COUNTRIES)[number]];
    return digits ? new AsYouType(country).input(digits) : "";
}

interface CountryOption {
    code: CountryCode;
    name: string;
    callingCode: string;
    flag: string;
}

function buildCountryOptions(language: string): CountryOption[] {
    let displayNames: Intl.DisplayNames | null = null;

    try {
        displayNames = new Intl.DisplayNames([language], { type: "region" });
    } catch {
        // Falls back to the raw ISO code below for a language tag Intl can't resolve.
    }

    return SUPPORTED_COUNTRIES.map((code) => ({
        code,
        name: displayNames?.of(code) ?? code,
        callingCode: getCountryCallingCode(code),
        flag: COUNTRY_FLAGS[code],
    })).sort((a, b) => a.name.localeCompare(b.name, language));
}

function onlyDigits(value: string): string {
    return value.replace(/\D/g, "");
}

// Number of digit characters in `text` before `position`.
function digitsBefore(text: string, position: number): number {
    let count = 0;

    for (let index = 0; index < position; index += 1) {
        if (/\d/.test(text[index])) {
            count += 1;
        }
    }

    return count;
}

// The position right after the `count`-th digit in `text` (1-indexed), i.e. where the
// caret should land once that many digits precede it.
function positionAfterDigit(text: string, count: number): number {
    if (count <= 0) {
        return 0;
    }

    let seen = 0;

    for (let index = 0; index < text.length; index += 1) {
        if (/\d/.test(text[index])) {
            seen += 1;

            if (seen === count) {
                return index + 1;
            }
        }
    }

    return text.length;
}

// Trims trailing digits until the number is no longer too long for `country` — using the
// library's own per-country length metadata (correct even for Italy's variable-length
// numbers) instead of a hand-maintained max-digits table.
function clampToMaxLength(country: CountryCode, digits: string): string {
    let candidate = digits;

    while (
        candidate.length > 0 &&
        validatePhoneNumberLength(candidate, country) === "TOO_LONG"
    ) {
        candidate = candidate.slice(0, -1);
    }

    return candidate;
}

// Formats `digits` for `country` and returns the best current E.164 guess the library can
// produce from the same formatter pass — falls back to a plain concatenation while there
// aren't yet enough digits for the library to resolve a full number.
function format(country: CountryCode, digits: string) {
    const formatter = new AsYouType(country);
    const display = formatter.input(digits);
    const parsed = formatter.getNumber();
    const e164 = parsed?.number ?? (digits ? `+${getCountryCallingCode(country)}${digits}` : "");

    return { display, e164 };
}

function deriveFromValue(value: string): { country: CountryCode; digits: string } {
    if (!value) {
        return { country: DEFAULT_COUNTRY, digits: "" };
    }

    const formatter = new AsYouType();
    formatter.input(value);
    const parsed = formatter.getNumber();

    if (
        parsed?.country &&
        (SUPPORTED_COUNTRIES as readonly CountryCode[]).includes(parsed.country)
    ) {
        return { country: parsed.country, digits: parsed.nationalNumber };
    }

    return { country: DEFAULT_COUNTRY, digits: onlyDigits(value) };
}

const dropdownButtonClassName =
    "flex items-center gap-1 rounded-lg border border-gray-300 bg-white px-2 py-2 hover:bg-gray-50";

interface PhoneInputProps {
    id: string;
    label: string;
    countrySelectLabel: string;
    value: string;
    onChange: (value: string) => void;
    error?: string;
    required?: boolean;
}

export function PhoneInput({
    id,
    label,
    countrySelectLabel,
    value,
    onChange,
    error,
    required = false,
}: PhoneInputProps) {
    const { language } = useLanguage();
    const [country, setCountry] = useState<CountryCode>(
        () => deriveFromValue(value).country,
    );
    const [digits, setDigits] = useState(() => deriveFromValue(value).digits);
    const lastEmitted = useRef(value);
    const inputRef = useRef<HTMLInputElement>(null);
    const pendingCaret = useRef<number | null>(null);

    useEffect(() => {
        if (value !== lastEmitted.current) {
            const derived = deriveFromValue(value);
            setCountry(derived.country);
            setDigits(derived.digits);
            lastEmitted.current = value;
        }
    }, [value]);

    const options = useMemo(() => buildCountryOptions(language), [language]);
    const current = options.find((option) => option.code === country) ?? options[0];
    const { display } = format(country, digits);

    useLayoutEffect(() => {
        if (pendingCaret.current !== null) {
            inputRef.current?.setSelectionRange(pendingCaret.current, pendingCaret.current);
            pendingCaret.current = null;
        }
    }, [display]);

    const emit = (nextCountry: CountryCode, nextDigits: string) => {
        const { e164 } = format(nextCountry, nextDigits);
        lastEmitted.current = e164;
        onChange(e164);
    };

    // Changing the country always starts the number over, rather than trying to carry
    // over and re-clamp the previous digits — a different country's number isn't a
    // truncated/extended version of the old one, and keeping stale digits around produced
    // confusing, hard-to-predict results.
    const selectCountry = (nextCountry: CountryCode) => {
        setCountry(nextCountry);
        setDigits("");
        emit(nextCountry, "");
    };

    const onDigitsChange = (event: ChangeEvent<HTMLInputElement>) => {
        let nextDigits = onlyDigits(event.target.value);
        const callingCode = getCountryCallingCode(country);

        if (nextDigits.startsWith(callingCode)) {
            nextDigits = nextDigits.slice(callingCode.length);
        }

        nextDigits = clampToMaxLength(country, nextDigits);

        setDigits(nextDigits);
        emit(country, nextDigits);
    };

    // Backspace/Delete right next to a mask literal (the ")" after a Brazilian/US area
    // code, the "-" before the last block, etc.) would otherwise just remove that literal
    // — the digits underneath are unchanged, so the mask immediately puts it right back,
    // making deletion feel stuck right where a wrong area code needs fixing. Skip over the
    // literal and remove the adjacent digit instead, in whichever direction the user is
    // deleting.
    const onKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
        if (event.key !== "Backspace" && event.key !== "Delete") {
            return;
        }

        const target = event.currentTarget;
        const { selectionStart, selectionEnd } = target;

        if (selectionStart === null || selectionEnd === null || selectionStart !== selectionEnd) {
            // A real selection (or an unsupported input type) deletes normally — the
            // existing onChange digit-extraction already handles that correctly.
            return;
        }

        const caret = selectionStart;
        const removingBackward = event.key === "Backspace";
        const charIndex = removingBackward ? caret - 1 : caret;

        if (charIndex < 0 || charIndex >= display.length || /\d/.test(display[charIndex])) {
            // Nothing there, or it's a real digit — let the default behavior run.
            return;
        }

        const digitCountBeforeCaret = digitsBefore(display, caret);
        const digitIndexToRemove = removingBackward ? digitCountBeforeCaret - 1 : digitCountBeforeCaret;

        if (digitIndexToRemove < 0 || digitIndexToRemove >= digits.length) {
            return;
        }

        event.preventDefault();

        const nextDigits = digits.slice(0, digitIndexToRemove) + digits.slice(digitIndexToRemove + 1);
        const { display: nextDisplay } = format(country, nextDigits);
        pendingCaret.current = positionAfterDigit(nextDisplay, digitIndexToRemove);

        setDigits(nextDigits);
        emit(country, nextDigits);
    };

    return (
        <FormField id={id} label={label} required={required} error={error}>
            <div className="flex gap-2">
                <div className="shrink-0">
                    <Dropdown
                        buttonClassName={dropdownButtonClassName}
                        label={
                            current && (
                                <img
                                    src={current.flag}
                                    alt={`${countrySelectLabel}: ${current.name} (+${current.callingCode})`}
                                    width={24}
                                    height={16}
                                    className="rounded-sm"
                                />
                            )
                        }
                    >
                        {(close) => (
                            <>
                                <p className="px-4 py-2 text-xs font-semibold uppercase text-gray-500">
                                    {countrySelectLabel}
                                </p>
                                {options.map((option) => (
                                    <button
                                        key={option.code}
                                        type="button"
                                        role="menuitem"
                                        aria-current={option.code === country}
                                        onClick={() => {
                                            selectCountry(option.code);
                                            close();
                                        }}
                                        className={`flex w-full items-center gap-2 px-4 py-2 text-left hover:bg-gray-100 ${
                                            option.code === country
                                                ? "font-semibold text-blue-600"
                                                : ""
                                        }`}
                                    >
                                        <img
                                            src={option.flag}
                                            alt=""
                                            width={20}
                                            height={14}
                                            className="rounded-sm"
                                        />
                                        {option.name} (+{option.callingCode})
                                    </button>
                                ))}
                            </>
                        )}
                    </Dropdown>
                </div>
                <input
                    ref={inputRef}
                    id={id}
                    name={id}
                    type="tel"
                    autoComplete="tel-national"
                    value={display}
                    onChange={onDigitsChange}
                    onKeyDown={onKeyDown}
                    required={required}
                    placeholder={placeholderFor(country)}
                    aria-invalid={error !== undefined}
                    aria-describedby={error ? `${id}-error` : undefined}
                    className={`${inputClassName(error !== undefined)} min-w-0 flex-1`}
                />
            </div>
        </FormField>
    );
}
