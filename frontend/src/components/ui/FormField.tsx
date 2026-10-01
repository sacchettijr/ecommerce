import type { ReactNode } from "react";

interface FormFieldProps {
    id: string;
    label: string;
    required?: boolean;
    error?: string;
    children: ReactNode;
}

export function FormField({
    id,
    label,
    required = false,
    error,
    children,
}: FormFieldProps) {
    return (
        <div className="mb-4">
            <label
                htmlFor={id}
                className="mb-1 block text-sm font-medium text-gray-700"
            >
                {label}
                {required && (
                    <span className="ml-0.5 text-red-600" aria-hidden="true">
                        *
                    </span>
                )}
            </label>
            {children}
            {error && (
                <p id={`${id}-error`} className="mt-1 text-sm text-red-600">
                    {error}
                </p>
            )}
        </div>
    );
}
