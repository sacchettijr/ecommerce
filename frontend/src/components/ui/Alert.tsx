import type { ReactNode } from "react";

import { CloseIcon } from "./icons.tsx";

export type AlertVariant = "error" | "success" | "info" | "warning";

const variantClassName: Record<AlertVariant, string> = {
    error: "bg-red-50 text-red-800 ring-red-200",
    success: "bg-green-50 text-green-800 ring-green-200",
    info: "bg-blue-50 text-blue-800 ring-blue-200",
    warning: "bg-yellow-50 text-yellow-800 ring-yellow-200",
};

type AlertProps = {
    variant: AlertVariant;
    children: ReactNode;
} & (
    | { onDismiss?: undefined; dismissLabel?: undefined }
    | { onDismiss: () => void; dismissLabel: string }
);

export function Alert({
    variant,
    children,
    onDismiss,
    dismissLabel,
}: AlertProps) {
    // Erros e avisos interrompem o leitor de tela; sucesso e informação são anunciados sem interromper.
    const role =
        variant === "error" || variant === "warning" ? "alert" : "status";

    return (
        <div
            role={role}
            className={`mb-4 flex items-start gap-3 rounded-lg p-4 ring-1 ${variantClassName[variant]}`}
        >
            <div className="flex-1">{children}</div>
            {onDismiss && (
                <button
                    type="button"
                    onClick={onDismiss}
                    aria-label={dismissLabel}
                    className="-m-1 shrink-0 rounded p-1 hover:bg-black/5"
                >
                    <CloseIcon className="size-4" />
                </button>
            )}
        </div>
    );
}
