import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router";

import type { SessionUser } from "../api/types.ts";
import { AuthContext } from "../context/AuthContext.ts";
import { makeSessionUser } from "../test/fixtures.ts";
import { ProtectedRoute } from "./ProtectedRoute.tsx";

function renderProtectedRoute(user: SessionUser | null, loading: boolean) {
    return render(
        <AuthContext value={{ user, loading, setUser: () => {} }}>
            <MemoryRouter initialEntries={["/profile"]}>
                <Routes>
                    <Route
                        path="/profile"
                        element={
                            <ProtectedRoute>
                                <p>Private content</p>
                            </ProtectedRoute>
                        }
                    />
                    <Route path="/login" element={<p>Login page</p>} />
                </Routes>
            </MemoryRouter>
        </AuthContext>,
    );
}

describe("ProtectedRoute", () => {
    it("renders nothing while the session is still loading", () => {
        const { container } = renderProtectedRoute(null, true);

        expect(container).toBeEmptyDOMElement();
    });

    it("redirects to the login page, preserving the next path, when there is no user", () => {
        renderProtectedRoute(null, false);

        expect(screen.getByText("Login page")).toBeInTheDocument();
        expect(screen.queryByText("Private content")).not.toBeInTheDocument();
    });

    it("renders the protected content when a user is authenticated", () => {
        renderProtectedRoute(makeSessionUser(), false);

        expect(screen.getByText("Private content")).toBeInTheDocument();
    });
});
