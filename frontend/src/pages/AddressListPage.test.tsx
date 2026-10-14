import { beforeEach, describe, expect, it, vi } from "vitest";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { fetchUserAddresses, setPrimaryAddress } from "../api/addresses.ts";
import { makeSessionUser, makeUserAddress } from "../test/fixtures.ts";
import { renderWithProviders } from "../test/renderWithProviders.tsx";
import { translations } from "../i18n/locales/index.ts";
import { AddressListPage } from "./AddressListPage.tsx";

vi.mock("../api/addresses.ts", () => ({
    fetchUserAddresses: vi.fn(),
    setPrimaryAddress: vi.fn(),
}));

const mockedFetch = vi.mocked(fetchUserAddresses);
const mockedSetPrimary = vi.mocked(setPrimaryAddress);

describe("AddressListPage", () => {
    beforeEach(() => {
        mockedFetch.mockReset();
        mockedSetPrimary.mockReset();
    });

    it("shows a loading state before the addresses arrive", () => {
        mockedFetch.mockImplementation(() => new Promise(() => {}));

        renderWithProviders(<AddressListPage />, {
            user: makeSessionUser(),
        });

        expect(screen.getByText("Loading…")).toBeInTheDocument();
        expect(
            screen.queryByText("No addresses registered."),
        ).not.toBeInTheDocument();
    });

    it("shows an error notification, not the empty state, when the request fails", async () => {
        mockedFetch.mockRejectedValue(new Error("network down"));

        renderWithProviders(<AddressListPage />, {
            user: makeSessionUser(),
        });

        expect(
            await screen.findByText(
                "Could not load your addresses. Please try again.",
            ),
        ).toBeInTheDocument();
        expect(
            screen.queryByText("No addresses registered."),
        ).not.toBeInTheDocument();
    });

    it("shows the exact empty-state message when the user has no addresses", async () => {
        mockedFetch.mockResolvedValue([]);

        renderWithProviders(<AddressListPage />, {
            user: makeSessionUser(),
        });

        expect(
            await screen.findByText("No addresses registered."),
        ).toBeInTheDocument();
    });

    it("keeps the required exact Portuguese empty-state message", () => {
        expect(translations["pt-br"].addressList.emptyState).toBe(
            "Nenhum endereço cadastrado.",
        );
    });

    it("shows the Add address action in the empty state", async () => {
        mockedFetch.mockResolvedValue([]);
        renderWithProviders(<AddressListPage />, { user: makeSessionUser() });
        expect(
            await screen.findByRole("button", { name: "Add address" }),
        ).toBeInTheDocument();
    });

    it("shows the Add address action in the populated state", async () => {
        mockedFetch.mockResolvedValue([makeUserAddress()]);
        renderWithProviders(<AddressListPage />, { user: makeSessionUser() });
        expect(
            await screen.findByRole("button", { name: "Add address" }),
        ).toBeInTheDocument();
    });

    it("renders only the fields that have a non-blank value, preserving a literal '0'", async () => {
        mockedFetch.mockResolvedValue([
            makeUserAddress({
                number: "0",
                complement: "",
                reference: "   ",
                district: "Centro",
            }),
        ]);

        renderWithProviders(<AddressListPage />, {
            user: makeSessionUser(),
        });

        await screen.findByText("Centro");
        expect(screen.getByText("Number")).toBeInTheDocument();
        expect(screen.getByText("0")).toBeInTheDocument();
        expect(screen.queryByText("Complement")).not.toBeInTheDocument();
        expect(screen.queryByText("Reference")).not.toBeInTheDocument();
    });

    it("checks the radio of the authoritative primary address", async () => {
        mockedFetch.mockResolvedValue([
            makeUserAddress({ id: 1, street: "First", primary: true }),
            makeUserAddress({ id: 2, street: "Second", primary: false }),
        ]);

        renderWithProviders(<AddressListPage />, {
            user: makeSessionUser(),
        });

        const firstRadio = await screen.findByRole("radio", {
            name: "Set First, 100 as primary address",
        });
        const secondRadio = screen.getByRole("radio", {
            name: "Set Second, 100 as primary address",
        });
        expect(firstRadio).toBeChecked();
        expect(secondRadio).not.toBeChecked();
    });

    it("selecting a different address calls the API with that address's id", async () => {
        const user = userEvent.setup();
        mockedFetch.mockResolvedValue([
            makeUserAddress({ id: 1, street: "First", primary: true }),
            makeUserAddress({ id: 2, street: "Second", primary: false }),
        ]);
        mockedSetPrimary.mockResolvedValue([
            makeUserAddress({ id: 1, street: "First", primary: false }),
            makeUserAddress({ id: 2, street: "Second", primary: true }),
        ]);

        renderWithProviders(<AddressListPage />, {
            user: makeSessionUser(),
        });

        const secondRadio = await screen.findByRole("radio", {
            name: "Set Second, 100 as primary address",
        });
        await user.click(secondRadio);

        expect(mockedSetPrimary).toHaveBeenCalledWith(2, expect.anything());
        expect(
            await screen.findByText("Primary address updated successfully."),
        ).toBeInTheDocument();
        expect(secondRadio).toBeChecked();
    });

    it("reconciles with the authoritative list and shows an error when the update fails", async () => {
        const user = userEvent.setup();
        mockedFetch.mockResolvedValueOnce([
            makeUserAddress({ id: 1, street: "First", primary: true }),
            makeUserAddress({ id: 2, street: "Second", primary: false }),
        ]);
        mockedSetPrimary.mockRejectedValue(new Error("boom"));
        mockedFetch.mockResolvedValueOnce([
            makeUserAddress({ id: 1, street: "First", primary: true }),
            makeUserAddress({ id: 2, street: "Second", primary: false }),
        ]);

        renderWithProviders(<AddressListPage />, {
            user: makeSessionUser(),
        });

        const secondRadio = await screen.findByRole("radio", {
            name: "Set Second, 100 as primary address",
        });
        await user.click(secondRadio);

        expect(
            await screen.findByText(
                "Could not update your primary address. Please try again.",
            ),
        ).toBeInTheDocument();
        const firstRadio = screen.getByRole("radio", {
            name: "Set First, 100 as primary address",
        });
        expect(firstRadio).toBeChecked();
        expect(secondRadio).not.toBeChecked();
    });

    it("ignores a stale response once a newer selection has started", async () => {
        const user = userEvent.setup();
        mockedFetch.mockResolvedValue([
            makeUserAddress({ id: 1, street: "First", primary: true }),
            makeUserAddress({ id: 2, street: "Second", primary: false }),
            makeUserAddress({ id: 3, street: "Third", primary: false }),
        ]);

        let resolveFirstClick: (value: ReturnType<typeof makeUserAddress>[]) => void =
            () => {};
        let resolveSecondClick: (value: ReturnType<typeof makeUserAddress>[]) => void =
            () => {};
        mockedSetPrimary
            .mockImplementationOnce(
                () =>
                    new Promise((resolve) => {
                        resolveFirstClick = resolve;
                    }),
            )
            .mockImplementationOnce(
                () =>
                    new Promise((resolve) => {
                        resolveSecondClick = resolve;
                    }),
            );

        renderWithProviders(<AddressListPage />, {
            user: makeSessionUser(),
        });

        const secondRadio = await screen.findByRole("radio", {
            name: "Set Second, 100 as primary address",
        });
        const thirdRadio = screen.getByRole("radio", {
            name: "Set Third, 100 as primary address",
        });

        await user.click(secondRadio);
        await user.click(thirdRadio);

        // The newer (third) request settles first with its own authoritative result...
        resolveSecondClick([
            makeUserAddress({ id: 1, street: "First", primary: false }),
            makeUserAddress({ id: 2, street: "Second", primary: false }),
            makeUserAddress({ id: 3, street: "Third", primary: true }),
        ]);
        await screen.findByText("Primary address updated successfully.");
        expect(thirdRadio).toBeChecked();

        // ...and the older (second) request's late response must not override it.
        resolveFirstClick([
            makeUserAddress({ id: 1, street: "First", primary: false }),
            makeUserAddress({ id: 2, street: "Second", primary: true }),
            makeUserAddress({ id: 3, street: "Third", primary: false }),
        ]);
        await new Promise((resolve) => setTimeout(resolve, 0));

        expect(thirdRadio).toBeChecked();
        expect(secondRadio).not.toBeChecked();
    });

    it("Edit and Delete are inert: no API call, no navigation-implying callback", async () => {
        const user = userEvent.setup();
        mockedFetch.mockResolvedValue([makeUserAddress()]);

        renderWithProviders(<AddressListPage />, {
            user: makeSessionUser(),
        });

        const editButton = await screen.findByRole("button", {
            name: "Edit address",
        });
        const deleteButton = screen.getByRole("button", {
            name: "Delete address",
        });
        expect(editButton).toHaveAttribute("aria-disabled", "true");
        expect(deleteButton).toHaveAttribute("aria-disabled", "true");

        await user.click(editButton);
        await user.click(deleteButton);

        expect(mockedSetPrimary).not.toHaveBeenCalled();
        expect(mockedFetch).toHaveBeenCalledTimes(1);
    });

    it("exposes translated, accessible tooltips for the icon actions", async () => {
        mockedFetch.mockResolvedValue([makeUserAddress()]);

        renderWithProviders(<AddressListPage />, {
            user: makeSessionUser(),
        });

        const editButton = await screen.findByRole("button", {
            name: "Edit address",
        });
        const describedBy = editButton.getAttribute("aria-describedby");
        expect(describedBy).not.toBeNull();
        const tooltip = within(editButton.parentElement as HTMLElement).getByRole(
            "tooltip",
        );
        expect(tooltip).toHaveTextContent("Edit address");
        expect(tooltip.id).toBe(describedBy);
    });
});
