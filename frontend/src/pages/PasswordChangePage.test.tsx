import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { changePassword } from "../api/auth.ts";
import { ApiError } from "../api/client.ts";
import { makeSessionUser } from "../test/fixtures.ts";
import { renderWithProviders } from "../test/renderWithProviders.tsx";
import { PasswordChangePage } from "./PasswordChangePage.tsx";

vi.mock("../api/auth.ts", () => ({
    changePassword: vi.fn(),
}));

const mockedChangePassword = vi.mocked(changePassword);

// Required fields append a visible "*" to the <label>'s text content (FormField.tsx), so an
// exact-string match on the label text alone would never find them.
function byLabel(text: string): RegExp {
    return new RegExp(`^${text}`);
}

async function fillAndSubmit(
    user: ReturnType<typeof userEvent.setup>,
    { old = "x", new1 = "y", new2 = "y" } = {},
) {
    await user.type(screen.getByLabelText(byLabel("Current password")), old);
    await user.type(screen.getByLabelText(byLabel("New password")), new1);
    await user.type(
        screen.getByLabelText(byLabel("Confirm new password")),
        new2,
    );
    await user.click(screen.getByRole("button", { name: "Save" }));
}

describe("PasswordChangePage", () => {
    beforeEach(() => {
        mockedChangePassword.mockReset();
    });

    it("renders the current, new and confirm password fields", () => {
        renderWithProviders(<PasswordChangePage />, {
            user: makeSessionUser(),
        });

        expect(
            screen.getByLabelText(byLabel("Current password")),
        ).toBeInTheDocument();
        expect(
            screen.getByLabelText(byLabel("New password")),
        ).toBeInTheDocument();
        expect(
            screen.getByLabelText(byLabel("Confirm new password")),
        ).toBeInTheDocument();
    });

    it("submits the entered values, shows success feedback and clears the fields", async () => {
        mockedChangePassword.mockResolvedValue(undefined);
        const user = userEvent.setup();

        renderWithProviders(<PasswordChangePage />, {
            user: makeSessionUser(),
        });

        await fillAndSubmit(user, {
            old: "OldPass123!",
            new1: "NewPass456!",
            new2: "NewPass456!",
        });

        expect(mockedChangePassword).toHaveBeenCalledWith(
            "OldPass123!",
            "NewPass456!",
            "NewPass456!",
        );
        expect(
            await screen.findByText(
                "Your password has been changed successfully.",
            ),
        ).toBeInTheDocument();
        expect(screen.getByLabelText(byLabel("Current password"))).toHaveValue(
            "",
        );
        expect(screen.getByLabelText(byLabel("New password"))).toHaveValue(
            "",
        );
        expect(
            screen.getByLabelText(byLabel("Confirm new password")),
        ).toHaveValue("");
    });

    it("shows a field-level error next to the current password input and preserves other values", async () => {
        mockedChangePassword.mockRejectedValue(
            new ApiError(400, {
                old_password: ["Your old password was entered incorrectly."],
            }),
        );
        const user = userEvent.setup();

        renderWithProviders(<PasswordChangePage />, {
            user: makeSessionUser(),
        });

        await fillAndSubmit(user, { old: "wrong", new1: "NewPass456!" });

        expect(
            await screen.findByText(
                "Your old password was entered incorrectly.",
            ),
        ).toBeInTheDocument();
        expect(screen.getByLabelText(byLabel("New password"))).toHaveValue(
            "NewPass456!",
        );
    });

    it("shows a form-level error through the shared alert mechanism", async () => {
        mockedChangePassword.mockRejectedValue(
            new ApiError(400, { non_field_errors: ["Something went wrong."] }),
        );
        const user = userEvent.setup();

        renderWithProviders(<PasswordChangePage />, {
            user: makeSessionUser(),
        });

        await fillAndSubmit(user);

        expect(
            await screen.findByText("Something went wrong."),
        ).toBeInTheDocument();
    });

    it("disables the submit button while the request is in flight", async () => {
        let resolveChange: () => void = () => {};
        mockedChangePassword.mockImplementation(
            () =>
                new Promise((resolve) => {
                    resolveChange = () => resolve(undefined);
                }),
        );
        const user = userEvent.setup();

        renderWithProviders(<PasswordChangePage />, {
            user: makeSessionUser(),
        });

        await fillAndSubmit(user);

        expect(screen.getByRole("button", { name: "Saving…" })).toBeDisabled();
        resolveChange();
    });
});
