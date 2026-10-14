import { describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { makeSessionUser } from "../../test/fixtures.ts";
import { renderWithProviders } from "../../test/renderWithProviders.tsx";
import { AccountLayout } from "./AccountLayout.tsx";

describe("AccountLayout", () => {
    it("renders the account navigation and the page content", () => {
        renderWithProviders(
            <AccountLayout title="Account">
                <p>Profile content</p>
            </AccountLayout>,
            { user: makeSessionUser() },
        );

        expect(
            screen.getByRole("navigation", { name: "Account navigation" }),
        ).toBeInTheDocument();
        expect(screen.getByRole("link", { name: "Profile" })).toHaveAttribute(
            "href",
            "/profile",
        );
        expect(screen.getByText("Profile content")).toBeInTheDocument();
    });

    it("links to the edit profile page", () => {
        renderWithProviders(
            <AccountLayout title="Account">
                <p>Profile content</p>
            </AccountLayout>,
            { user: makeSessionUser() },
        );

        expect(
            screen.getByRole("link", { name: /edit profile/i }),
        ).toHaveAttribute("href", "/profile/edit");
    });

    it("links to the password change page", () => {
        renderWithProviders(
            <AccountLayout title="Account">
                <p>Profile content</p>
            </AccountLayout>,
            { user: makeSessionUser() },
        );

        expect(
            screen.getByRole("link", { name: /change password/i }),
        ).toHaveAttribute("href", "/profile/password");
    });

    it("renders the remaining account items as inert (no destination yet)", () => {
        renderWithProviders(
            <AccountLayout title="Account">
                <p>Profile content</p>
            </AccountLayout>,
            { user: makeSessionUser() },
        );

        expect(
            screen.queryByRole("link", { name: /my orders/i }),
        ).not.toBeInTheDocument();
        expect(screen.getByText("My orders")).toBeInTheDocument();
        expect(screen.getByText("My addresses")).toBeInTheDocument();
        expect(screen.getByText("Wishlist")).toBeInTheDocument();
    });

    it("only shows the admin link when the user is staff", () => {
        renderWithProviders(
            <AccountLayout title="Account">
                <p>Profile content</p>
            </AccountLayout>,
            { user: makeSessionUser({ is_staff: false }) },
        );
        expect(
            screen.queryByRole("link", { name: /admin/i }),
        ).not.toBeInTheDocument();
    });

    it("shows the admin link when the user is staff", () => {
        renderWithProviders(
            <AccountLayout title="Account">
                <p>Profile content</p>
            </AccountLayout>,
            { user: makeSessionUser({ is_staff: true }) },
        );
        expect(screen.getByRole("link", { name: /admin/i })).toHaveAttribute(
            "href",
            "/admin/",
        );
    });

    it("renders messages and lets the user dismiss them", async () => {
        const user = userEvent.setup();
        const onDismissMessage = vi.fn();

        renderWithProviders(
            <AccountLayout
                title="Account"
                messages={[{ id: 1, variant: "success", text: "Saved!" }]}
                onDismissMessage={onDismissMessage}
            >
                <p>Profile content</p>
            </AccountLayout>,
            { user: makeSessionUser() },
        );

        expect(screen.getByText("Saved!")).toBeInTheDocument();

        await user.click(screen.getByRole("button", { name: "Dismiss" }));

        expect(onDismissMessage).toHaveBeenCalledWith(1);
    });
});
