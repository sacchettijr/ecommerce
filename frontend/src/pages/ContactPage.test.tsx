import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { sendContact } from "../api/contact.ts";
import { ApiError } from "../api/client.ts";
import { renderWithProviders } from "../test/renderWithProviders.tsx";
import { ContactPage } from "./ContactPage.tsx";

vi.mock("../api/contact.ts", () => ({
    sendContact: vi.fn(),
}));

const mockedSendContact = vi.mocked(sendContact);

async function fillValidFormExceptPhone(user: ReturnType<typeof userEvent.setup>) {
    await user.type(screen.getByLabelText(/^Name/), "Jane Doe");
    await user.type(screen.getByLabelText(/^Email/), "jane@example.com");
    await user.type(
        screen.getByLabelText(/^Message/),
        "Hello, I would like more information.",
    );
}

beforeEach(() => {
    mockedSendContact.mockReset();
    localStorage.clear();
});

afterEach(() => {
    vi.useRealTimers();
});

describe("ContactPage", () => {
    it("renders a country selector alongside the phone field", () => {
        renderWithProviders(<ContactPage />);

        expect(screen.getByLabelText(/^Phone/)).toBeInTheDocument();
        expect(
            screen.getByRole("button", { name: /Country code: Brazil/ }),
        ).toBeInTheDocument();
    });

    it(
        "submits a normalized E.164 phone number and clears the form on success",
        async () => {
            const user = userEvent.setup();
            mockedSendContact.mockResolvedValue(undefined);
            renderWithProviders(<ContactPage />);

            await fillValidFormExceptPhone(user);
            await user.type(screen.getByLabelText(/^Phone/), "11987654321");
            await user.click(screen.getByRole("button", { name: "Send" }));

            expect(mockedSendContact).toHaveBeenCalledWith(
                expect.objectContaining({ phone: "+5511987654321" }),
            );
            expect(
                await screen.findByText(/Message sent successfully/),
            ).toBeInTheDocument();
            expect(screen.getByLabelText(/^Name/)).toHaveValue("");
        },
        15000,
    );

    it("rejects an invalid phone number client-side using the library's own validity check", async () => {
        const user = userEvent.setup();
        renderWithProviders(<ContactPage />);

        await fillValidFormExceptPhone(user);
        await user.type(screen.getByLabelText(/^Phone/), "123");
        await user.click(screen.getByRole("button", { name: "Send" }));

        expect(
            await screen.findByText("Enter a valid phone number, with area code."),
        ).toBeInTheDocument();
        expect(mockedSendContact).not.toHaveBeenCalled();
    });

    it("shows a countdown on a 429, disables submit, ticks down, and preserves field values", async () => {
        vi.useFakeTimers({ shouldAdvanceTime: true });
        const user = userEvent.setup();
        mockedSendContact.mockRejectedValue(
            new ApiError(429, {
                code: "contact_cooldown",
                detail: "Please wait 3 seconds before sending another message.",
                retry_after: 3,
            }),
        );
        renderWithProviders(<ContactPage />);

        await fillValidFormExceptPhone(user);
        await user.type(screen.getByLabelText(/^Phone/), "11987654321");
        await user.click(screen.getByRole("button", { name: "Send" }));

        expect(
            await screen.findByText(
                "Please wait 3 seconds before sending another message.",
            ),
        ).toBeInTheDocument();
        expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
        expect(screen.getByLabelText(/^Name/)).toHaveValue("Jane Doe");

        await vi.advanceTimersByTimeAsync(3000);

        expect(
            screen.queryByText(
                "Please wait 3 seconds before sending another message.",
            ),
        ).not.toBeInTheDocument();
        expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
    });

    it("resumes an active cooldown after a reload instead of showing an enabled button", () => {
        localStorage.setItem(
            "contact_cooldown_until",
            String(Date.now() + 10_000),
        );

        renderWithProviders(<ContactPage />);

        expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
        expect(
            screen.getByText(/Please wait \d+ seconds before sending another message\./),
        ).toBeInTheDocument();
    });

    it("does not show a stale cooldown once it has already expired", () => {
        localStorage.setItem(
            "contact_cooldown_until",
            String(Date.now() - 1000),
        );

        renderWithProviders(<ContactPage />);

        expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
    });
});
