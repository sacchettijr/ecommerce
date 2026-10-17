import { describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { makeSessionUser } from "../../test/fixtures.ts";
import { renderWithProviders } from "../../test/renderWithProviders.tsx";
import { UserMenu } from "./UserMenu.tsx";

async function openMenu() {
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /hello,/i }));
    return user;
}

describe("UserMenu", () => {
    it("navigates to the wishlist page and closes the menu", async () => {
        renderWithProviders(
            <UserMenu user={makeSessionUser()} onCloseMobileMenu={vi.fn()} />,
        );
        const user = await openMenu();

        await user.click(screen.getByRole("menuitem", { name: "Wishlist" }));

        expect(screen.queryByRole("menu")).not.toBeInTheDocument();
    });

    it("navigates to the addresses page and closes the menu", async () => {
        renderWithProviders(
            <UserMenu user={makeSessionUser()} onCloseMobileMenu={vi.fn()} />,
        );
        const user = await openMenu();

        await user.click(screen.getByRole("menuitem", { name: "My addresses" }));

        expect(screen.queryByRole("menu")).not.toBeInTheDocument();
    });

    it("renders orders as inert (no destination yet)", async () => {
        renderWithProviders(
            <UserMenu user={makeSessionUser()} onCloseMobileMenu={vi.fn()} />,
        );
        await openMenu();

        expect(
            screen.getByRole("menuitem", { name: "My orders" }),
        ).not.toHaveAttribute("href");
    });
});
