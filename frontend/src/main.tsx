import "./index.css";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";

import App from "./App.tsx";
import { AuthProvider } from "./context/AuthProvider.tsx";
import { CartProvider } from "./context/CartProvider.tsx";
import { CategoriesProvider } from "./context/CategoriesProvider.tsx";
import { WishlistProvider } from "./context/WishlistProvider.tsx";
import { LanguageProvider } from "./i18n/LanguageProvider.tsx";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <BrowserRouter>
            <LanguageProvider>
                <AuthProvider>
                    <CartProvider>
                        <WishlistProvider>
                            <CategoriesProvider>
                                <App />
                            </CategoriesProvider>
                        </WishlistProvider>
                    </CartProvider>
                </AuthProvider>
            </LanguageProvider>
        </BrowserRouter>
    </StrictMode>,
);
