import { Route, Routes } from "react-router";

import { Layout } from "./components/layout/Layout.tsx";
import { ContactPage } from "./pages/ContactPage.tsx";
import { EmailVerificationConfirmPage } from "./pages/EmailVerificationConfirmPage.tsx";
import { HomePage } from "./pages/HomePage.tsx";
import { LoggedOutPage } from "./pages/LoggedOutPage.tsx";
import { LoginPage } from "./pages/LoginPage.tsx";
import { NotFoundPage } from "./pages/NotFoundPage.tsx";
import { PasswordResetCompletePage } from "./pages/PasswordResetCompletePage.tsx";
import { PasswordResetConfirmPage } from "./pages/PasswordResetConfirmPage.tsx";
import { PasswordResetDonePage } from "./pages/PasswordResetDonePage.tsx";
import { PasswordResetPage } from "./pages/PasswordResetPage.tsx";
import { ProductDetailPage } from "./pages/ProductDetailPage.tsx";
import { ProductListPage } from "./pages/ProductListPage.tsx";
import { SignupPage } from "./pages/SignupPage.tsx";

function App() {
    return (
        <Routes>
            <Route element={<Layout />}>
                <Route index element={<HomePage />} />
                <Route path="products" element={<ProductListPage />} />
                <Route path="category/:slug" element={<ProductListPage />} />
                <Route path="product/:slug" element={<ProductDetailPage />} />
                <Route path="contact" element={<ContactPage />} />
                <Route path="login" element={<LoginPage />} />
                <Route path="signup" element={<SignupPage />} />
                <Route path="logged-out" element={<LoggedOutPage />} />
                <Route
                    path="email-verification/:uid/:token"
                    element={<EmailVerificationConfirmPage />}
                />
                <Route path="password-reset" element={<PasswordResetPage />} />
                <Route
                    path="password-reset/done"
                    element={<PasswordResetDonePage />}
                />
                <Route
                    path="password-reset/confirm/:uid/:token"
                    element={<PasswordResetConfirmPage />}
                />
                <Route
                    path="password-reset/complete"
                    element={<PasswordResetCompletePage />}
                />
                <Route path="*" element={<NotFoundPage />} />
            </Route>
        </Routes>
    );
}

export default App;
