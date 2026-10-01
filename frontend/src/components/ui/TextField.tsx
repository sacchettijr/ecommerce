import type { ChangeEvent, HTMLInputAutoCompleteAttribute } from "react";

import { FormField } from "./FormField.tsx";
import { inputClassName } from "./inputClassName.ts";

interface TextFieldProps {
    name: string;
    label: string;
    type?: "text" | "email" | "password" | "date" | "tel";
    value: string;
    onChange: (event: ChangeEvent<HTMLInputElement>) => void;
    error?: string;
    required?: boolean;
    autoComplete?: HTMLInputAutoCompleteAttribute;
    placeholder?: string;
}

// Campo com <label>, mensagem de erro ligada ao input (aria-describedby) e aria-invalid.
export function TextField({
    name,
    label,
    type = "text",
    value,
    onChange,
    error,
    required = false,
    autoComplete,
    placeholder,
}: TextFieldProps) {
    return (
        <FormField id={name} label={label} required={required} error={error}>
            <input
                id={name}
                name={name}
                type={type}
                value={value}
                onChange={onChange}
                required={required}
                autoComplete={autoComplete}
                placeholder={placeholder}
                aria-invalid={error !== undefined}
                aria-describedby={error ? `${name}-error` : undefined}
                className={inputClassName(error !== undefined)}
            />
        </FormField>
    );
}
