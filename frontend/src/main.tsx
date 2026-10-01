import "./index.css";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";

import App from "./App.tsx";
import { AuthProvider } from "./context/AuthProvider.tsx";
import { CategoriesProvider } from "./context/CategoriesProvider.tsx";
import { LanguageProvider } from "./i18n/LanguageProvider.tsx";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <BrowserRouter>
            <LanguageProvider>
                <AuthProvider>
                    <CategoriesProvider>
                        <App />
                    </CategoriesProvider>
                </AuthProvider>
            </LanguageProvider>
        </BrowserRouter>
    </StrictMode>,
);
