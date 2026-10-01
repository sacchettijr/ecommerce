import type { ReactNode } from "react";

import { Alert } from "../ui/Alert.tsx";

interface AuthLayoutProps {
    title: string;
    heading: string;
    intro?: string;
    // Erros gerais do formulário (non_field_errors, credenciais inválidas, erro inesperado…).
    errors?: string[];
    // Mensagem positiva (e-mail enviado, senha alterada…).
    notice?: string;
    // Ações extras dentro do alerta de erro (ex.: reenviar o e-mail de confirmação).
    errorActions?: ReactNode;
    children?: ReactNode;
    links?: ReactNode;
    centered?: boolean;
}

// Estrutura visual compartilhada pelas páginas de autenticação
// (equivalente ao registration/base_login.html do Django).
export function AuthLayout({
    title,
    heading,
    intro,
    errors = [],
    notice,
    errorActions,
    children,
    links,
    centered = false,
}: AuthLayoutProps) {
    return (
        <>
            <title>{title}</title>

            <div className="mx-auto max-w-md px-4 py-12">
                <div className={centered ? "text-center" : undefined}>
                    <h1 className="mb-4 text-3xl font-bold">{heading}</h1>
                    {intro && <p className="mb-4 text-gray-600">{intro}</p>}
                </div>

                {notice && <Alert variant="success">{notice}</Alert>}
                {errors.length > 0 && (
                    <Alert variant="error">
                        {errors.map((message) => (
                            <p key={message}>{message}</p>
                        ))}
                        {errorActions}
                    </Alert>
                )}

                {children}

                {links && (
                    <div className={`mt-4 ${centered ? "text-center" : ""}`}>
                        {links}
                    </div>
                )}
            </div>
        </>
    );
}
