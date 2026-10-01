import { useState } from "react";

import { resendVerificationEmail } from "../../api/auth.ts";
import { useLanguage } from "../../i18n/useLanguage.ts";

type Status = "idle" | "sending" | "sent" | "error";

interface ResendConfirmationProps {
    email: string;
    next: string;
}

// Pede ao Django um novo e-mail de confirmação (quem envia o e-mail é sempre o backend).
export function ResendConfirmation({ email, next }: ResendConfirmationProps) {
    const { t } = useLanguage();
    const [status, setStatus] = useState<Status>("idle");

    const onClick = async () => {
        if (status === "sending") {
            return;
        }

        setStatus("sending");

        try {
            await resendVerificationEmail(email, next);
            setStatus("sent");
        } catch {
            setStatus("error");
        }
    };

    return (
        <div className="mt-2">
            <button
                type="button"
                onClick={onClick}
                disabled={status === "sending"}
                className="font-medium underline disabled:cursor-not-allowed disabled:opacity-60"
            >
                {status === "sending"
                    ? t.auth.login.resending
                    : t.auth.login.resendConfirmation}
            </button>
            {status === "sent" && (
                <p role="status" className="mt-2 text-sm">
                    {t.auth.login.confirmationResent}
                </p>
            )}
            {status === "error" && (
                <p role="alert" className="mt-2 text-sm">
                    {t.auth.errors.generic}
                </p>
            )}
        </div>
    );
}
