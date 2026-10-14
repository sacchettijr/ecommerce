import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { updateProfile } from "../api/auth.ts";
import { ApiError } from "../api/client.ts";
import { makeSessionUser } from "../test/fixtures.ts";
import { renderWithProviders } from "../test/renderWithProviders.tsx";
import { ProfileEditPage } from "./ProfileEditPage.tsx";

vi.mock("../api/auth.ts", () => ({
    updateProfile: vi.fn(),
}));

const mockedUpdateProfile = vi.mocked(updateProfile);

// Required fields append a visible "*" to the <label>'s text content (FormField.tsx), so an
// exact-string match on the label text alone would never find them.
function byLabel(text: string): RegExp {
    return new RegExp(`^${text}`);
}

describe("ProfileEditPage", () => {
    beforeEach(() => {
        mockedUpdateProfile.mockReset();
    });

    it("shows a loading state while the session is still resolving", () => {
        renderWithProviders(<ProfileEditPage />, { user: null, loading: true });

        expect(screen.getByText("Loading…")).toBeInTheDocument();
    });

    it("shows an error state instead of fabricated data when there is no user", () => {
        renderWithProviders(<ProfileEditPage />, { user: null, loading: false });

        expect(
            screen.getByText("Could not load your profile. Please try again."),
        ).toBeInTheDocument();
    });

    it("prefills the form with the authenticated user's own current data", () => {
        const user = makeSessionUser({
            name: "Jane Doe",
            date_birth: "1990-05-20",
            phone: "+5511987654321",
        });

        renderWithProviders(<ProfileEditPage />, { user });

        expect(screen.getByLabelText(byLabel("Full name"))).toHaveValue("Jane Doe");
        expect(screen.getByLabelText(byLabel("Date of birth"))).toHaveValue(
            "1990-05-20",
        );
        expect(screen.getByLabelText(byLabel("Phone"))).toHaveValue(
            "+5511987654321",
        );
    });

    it("does not render any control for staff/permission fields", () => {
        renderWithProviders(<ProfileEditPage />, {
            user: makeSessionUser({ is_staff: true }),
        });

        expect(screen.queryByLabelText(/staff/i)).not.toBeInTheDocument();
        expect(screen.queryByLabelText(/admin/i)).not.toBeInTheDocument();
        expect(screen.queryByLabelText(/active/i)).not.toBeInTheDocument();
    });

    it("submits the updated values, shows success feedback and refreshes the session state", async () => {
        const user = makeSessionUser({ name: "Jane Doe", phone: "" });
        const freshUser = makeSessionUser({
            name: "Jane Updated",
            phone: "+5511987654321",
        });
        mockedUpdateProfile.mockResolvedValue(freshUser);
        const setUser = vi.fn();
        const testUser = userEvent.setup();

        renderWithProviders(<ProfileEditPage />, { user, setUser });

        const nameField = screen.getByLabelText(byLabel("Full name"));
        await testUser.clear(nameField);
        await testUser.type(nameField, "Jane Updated");
        const phoneField = screen.getByLabelText(byLabel("Phone"));
        await testUser.type(phoneField, "11987654321");
        await testUser.click(
            screen.getByRole("button", { name: "Update profile" }),
        );

        expect(mockedUpdateProfile).toHaveBeenCalledWith({
            name: "Jane Updated",
            date_birth: user.date_birth,
            phone: "11987654321",
        });
        expect(
            await screen.findByText(
                "Your profile has been updated successfully.",
            ),
        ).toBeInTheDocument();
        // Refreshes the shared auth state so the navbar/profile home never show stale data.
        expect(setUser).toHaveBeenCalledWith(freshUser);
        // Reflects the server-confirmed (normalized) values, not raw input.
        expect(screen.getByLabelText(byLabel("Phone"))).toHaveValue(
            "+5511987654321",
        );
    });

    it("shows a field-level error next to the corresponding input and preserves other values", async () => {
        mockedUpdateProfile.mockRejectedValue(
            new ApiError(400, { name: ["The name must be 3 characters."] }),
        );
        const testUser = userEvent.setup();

        renderWithProviders(<ProfileEditPage />, {
            user: makeSessionUser({ name: "Jane Doe" }),
        });

        const nameField = screen.getByLabelText(byLabel("Full name"));
        await testUser.clear(nameField);
        await testUser.type(nameField, "Ab");
        await testUser.click(
            screen.getByRole("button", { name: "Update profile" }),
        );

        expect(
            await screen.findByText("The name must be 3 characters."),
        ).toBeInTheDocument();
        expect(screen.getByLabelText(byLabel("Full name"))).toHaveValue("Ab");
    });

    it("shows a form-level error through the shared alert mechanism and never a false success", async () => {
        mockedUpdateProfile.mockRejectedValue(
            new ApiError(400, { non_field_errors: ["Something went wrong."] }),
        );
        const testUser = userEvent.setup();

        renderWithProviders(<ProfileEditPage />, {
            user: makeSessionUser(),
        });

        await testUser.click(
            screen.getByRole("button", { name: "Update profile" }),
        );

        expect(
            await screen.findByText("Something went wrong."),
        ).toBeInTheDocument();
        expect(
            screen.queryByText("Your profile has been updated successfully."),
        ).not.toBeInTheDocument();
    });

    it("disables the submit button while the request is in flight", async () => {
        let resolveUpdate: () => void = () => {};
        mockedUpdateProfile.mockImplementation(
            () =>
                new Promise((resolve) => {
                    resolveUpdate = () => resolve(makeSessionUser());
                }),
        );
        const testUser = userEvent.setup();

        renderWithProviders(<ProfileEditPage />, {
            user: makeSessionUser(),
        });

        await testUser.click(
            screen.getByRole("button", { name: "Update profile" }),
        );

        expect(screen.getByRole("button", { name: "Saving…" })).toBeDisabled();
        resolveUpdate();
    });
});
