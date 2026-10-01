import type { ReactNode } from "react";

type AlertVariant = "error" | "success" | "info" | "warning";

const variantClassName: Record<AlertVariant, string> = {
    error: "bg-red-50 text-red-800 ring-red-200",
    success: "bg-green-50 text-green-800 ring-green-200",
    info: "bg-blue-50 text-blue-800 ring-blue-200",
    warning: "bg-yellow-50 text-yellow-800 ring-yellow-200",
};

interface AlertProps {
    variant: AlertVariant;
    children: ReactNode;
}

export function Alert({ variant, children }: AlertProps) {
    // Erros e avisos interrompem o leitor de tela; sucesso e informação são anunciados sem interromper.
    const role =
        variant === "error" || variant === "warning" ? "alert" : "status";

    return (
        <div
            role={role}
            className={`mb-4 rounded-lg p-4 ring-1 ${variantClassName[variant]}`}
        >
            {children}
        </div>
    );
}
