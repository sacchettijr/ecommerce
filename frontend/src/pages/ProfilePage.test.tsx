import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";

import { makeSessionUser } from "../test/fixtures.ts";
import { renderWithProviders } from "../test/renderWithProviders.tsx";
import { ProfilePage } from "./ProfilePage.tsx";

describe("ProfilePage", () => {
    it("shows a loading state while the session is still resolving", () => {
        renderWithProviders(<ProfilePage />, { user: null, loading: true });

        expect(screen.getByText("Loading…")).toBeInTheDocument();
    });

    it("shows an error state instead of fabricated data when there is no user", () => {
        renderWithProviders(<ProfilePage />, { user: null, loading: false });

        expect(
            screen.getByText("Could not load your profile. Please try again."),
        ).toBeInTheDocument();
        expect(screen.queryByText("Name")).not.toBeInTheDocument();
    });

    it("renders the authenticated user's own data", () => {
        const user = makeSessionUser({
            name: "Jane Doe",
            email: "jane@example.com",
            date_birth: "1990-05-20",
            phone: "",
            created_at: "2026-01-10T12:00:00-04:00",
            is_staff: false,
        });

        renderWithProviders(<ProfilePage />, { user });

        expect(screen.getByText("Jane Doe")).toBeInTheDocument();
        expect(screen.getByText("jane@example.com")).toBeInTheDocument();
        expect(
            screen.getByText(new Date(1990, 4, 20).toLocaleDateString("en")),
        ).toBeInTheDocument();
        expect(screen.getByText("Not provided")).toBeInTheDocument();
        expect(
            screen.getByText(
                new Date("2026-01-10T12:00:00-04:00").toLocaleDateString("en"),
            ),
        ).toBeInTheDocument();
        expect(screen.queryByText("Staff account")).not.toBeInTheDocument();
    });

    it("renders the phone number when one is set", () => {
        const user = makeSessionUser({ phone: "+5511987654321" });

        renderWithProviders(<ProfilePage />, { user });

        expect(screen.getByText("+5511987654321")).toBeInTheDocument();
        expect(screen.queryByText("Not provided")).not.toBeInTheDocument();
    });

    it("shows the staff badge only when is_staff is true", () => {
        const user = makeSessionUser({ is_staff: true });

        renderWithProviders(<ProfilePage />, { user });

        expect(screen.getByText("Staff account")).toBeInTheDocument();
    });

    it("never renders another user's data", () => {
        const user = makeSessionUser({
            name: "Jane Doe",
            email: "jane@example.com",
        });

        renderWithProviders(<ProfilePage />, { user });

        expect(screen.queryByText("Someone Else")).not.toBeInTheDocument();
        expect(
            screen.queryByText("someone-else@example.com"),
        ).not.toBeInTheDocument();
    });
});
