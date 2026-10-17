import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { signup } from "../api/auth.ts";
import { ApiError } from "../api/client.ts";
import { renderWithProviders } from "../test/renderWithProviders.tsx";
import { SignupPage } from "./SignupPage.tsx";

vi.mock("../api/auth.ts", () => ({
    signup: vi.fn(),
}));

const mockedSignup = vi.mocked(signup);

function byLabel(text: string): RegExp {
    return new RegExp(`^${text}`);
}

describe("SignupPage", () => {
    beforeEach(() => {
        mockedSignup.mockReset();
    });

    it("renders a country selector alongside the phone field", () => {
        renderWithProviders(<SignupPage />);

        expect(screen.getByLabelText(byLabel("Phone"))).toBeInTheDocument();
        expect(
            screen.getByRole("button", { name: /Country code: Brazil/ }),
        ).toBeInTheDocument();
    });

    it(
        "submits a normalized E.164 phone number",
        async () => {
            const user = userEvent.setup();
            mockedSignup.mockResolvedValue(undefined);
            renderWithProviders(<SignupPage />);

            await user.type(screen.getByLabelText(byLabel("Full name")), "Jane Doe");
            await user.type(screen.getByLabelText(byLabel("Email")), "jane@example.com");
            await user.type(screen.getByLabelText(byLabel("Date of birth")), "1990-05-20");
            await user.type(screen.getByLabelText(byLabel("Phone")), "11987654321");
            await user.type(screen.getByLabelText(byLabel("Password")), "Str0ng#Pass1");
            await user.type(
                screen.getByLabelText(byLabel("Confirm password")),
                "Str0ng#Pass1",
            );
            await user.click(screen.getByRole("button", { name: "Create account" }));

            expect(mockedSignup).toHaveBeenCalledWith(
                expect.objectContaining({ phone: "+5511987654321" }),
                expect.anything(),
            );
        },
        15000,
    );

    it("preserves other field values when the phone field has a server-side error", async () => {
        const user = userEvent.setup();
        mockedSignup.mockRejectedValue(
            new ApiError(400, { phone: ["Enter a valid phone number."] }),
        );
        renderWithProviders(<SignupPage />);

        await user.type(screen.getByLabelText(byLabel("Full name")), "Jane Doe");
        await user.type(screen.getByLabelText(byLabel("Phone")), "123");
        await user.click(screen.getByRole("button", { name: "Create account" }));

        expect(screen.getByLabelText(byLabel("Full name"))).toHaveValue("Jane Doe");
    });
});
