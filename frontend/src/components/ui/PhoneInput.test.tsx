import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { LanguageContext } from "../../i18n/LanguageContext.ts";
import { LANGUAGES } from "../../i18n/languages.ts";
import { translations } from "../../i18n/locales/index.ts";
import { renderWithProviders } from "../../test/renderWithProviders.tsx";
import { PhoneInput } from "./PhoneInput.tsx";

// PhoneInput only reads useLanguage() — a bare LanguageContext wrap (no router/auth) is
// enough, and keeps rerender() swapping props on the *same* mounted instance instead of
// remounting it, which is what the "re-syncs from an external value change" test needs.
function withLanguage(children: ReactNode) {
    return (
        <LanguageContext
            value={{
                language: "en",
                setLanguage: () => {},
                languages: LANGUAGES,
                t: translations.en,
            }}
        >
            {children}
        </LanguageContext>
    );
}

function Controlled({ initial = "" }: { initial?: string }) {
    const onChange = vi.fn();
    return (
        <PhoneInput
            id="phone"
            label="Phone"
            countrySelectLabel="Country code"
            value={initial}
            onChange={onChange}
        />
    );
}

function countryTrigger() {
    return screen.getByRole("button", { name: /^Country code:/ });
}

async function selectCountry(
    user: ReturnType<typeof userEvent.setup>,
    namePattern: RegExp,
) {
    await user.click(countryTrigger());
    await user.click(screen.getByRole("menuitem", { name: namePattern }));
}

describe("PhoneInput", () => {
    it("defaults to Brazil and masks digits as the user types", async () => {
        const user = userEvent.setup();
        renderWithProviders(<Controlled />);

        const input = screen.getByLabelText("Phone");
        await user.type(input, "11987654321");

        expect(input).toHaveValue("(11) 98765-4321");
        expect(countryTrigger()).toHaveAccessibleName(/Brazil \(\+55\)/);
    });

    it("strips letters and formatting characters, keeping only digits", async () => {
        const user = userEvent.setup();
        renderWithProviders(<Controlled />);

        const input = screen.getByLabelText("Phone");
        await user.type(input, "(11a) 9b8765-c4321");

        expect(input).toHaveValue("(11) 98765-4321");
    });

    it("emits a normalized E.164 value to the parent", async () => {
        const user = userEvent.setup();
        const onChange = vi.fn();
        renderWithProviders(
            <PhoneInput
                id="phone"
                label="Phone"
                countrySelectLabel="Country code"
                value=""
                onChange={onChange}
            />,
        );

        await user.type(screen.getByLabelText("Phone"), "11987654321");

        expect(onChange).toHaveBeenLastCalledWith("+5511987654321");
    });

    it("clears the previously-typed digits when the country is changed", async () => {
        const user = userEvent.setup();
        const onChange = vi.fn();
        renderWithProviders(
            <PhoneInput
                id="phone"
                label="Phone"
                countrySelectLabel="Country code"
                value=""
                onChange={onChange}
            />,
        );

        await user.type(screen.getByLabelText("Phone"), "2025551234");
        await selectCountry(user, /United States/);

        expect(screen.getByLabelText("Phone")).toHaveValue("");
        expect(onChange).toHaveBeenLastCalledWith("");
        expect(countryTrigger()).toHaveAccessibleName(/United States \(\+1\)/);
    });

    it("updates the phone field's placeholder to match the selected country", async () => {
        const user = userEvent.setup();
        renderWithProviders(<Controlled />);

        expect(screen.getByLabelText("Phone")).toHaveAttribute(
            "placeholder",
            "(69) 99123-4567",
        );

        await selectCountry(user, /United States/);

        expect(screen.getByLabelText("Phone")).toHaveAttribute(
            "placeholder",
            "(202) 555-1234",
        );
    });

    it("renders a non-Brazilian E.164 value with the matching country and mask", () => {
        renderWithProviders(<Controlled initial="+12025551234" />);

        expect(countryTrigger()).toHaveAccessibleName(/United States \(\+1\)/);
        expect(screen.getByLabelText("Phone")).toHaveValue("(202) 555-1234");
    });

    it("offers only the countries this site currently serves", async () => {
        const user = userEvent.setup();
        renderWithProviders(<Controlled />);

        await user.click(countryTrigger());

        const items = screen.getAllByRole("menuitem").map((item) => item.textContent);
        expect(items).toHaveLength(4);
        expect(items.join(" ")).toMatch(/Brazil/);
        expect(items.join(" ")).toMatch(/United States/);
        expect(items.join(" ")).toMatch(/France/);
        expect(items.join(" ")).toMatch(/Italy/);
    });

    it("does not accept more digits than Brazil's own number length allows", async () => {
        const user = userEvent.setup();
        renderWithProviders(<Controlled />);

        const input = screen.getByLabelText("Phone");
        await user.type(input, "699912345678999");

        expect(input).toHaveValue("(69) 99123-4567");
    });

    it("does not accept more digits than the US's own number length allows", async () => {
        const user = userEvent.setup();
        const onChange = vi.fn();
        renderWithProviders(
            <PhoneInput
                id="phone"
                label="Phone"
                countrySelectLabel="Country code"
                value=""
                onChange={onChange}
            />,
        );

        await selectCountry(user, /United States/);
        await user.type(screen.getByLabelText("Phone"), "20255512345999");

        expect(screen.getByLabelText("Phone")).toHaveValue("(202) 555-1234");
        expect(onChange).toHaveBeenLastCalledWith("+12025551234");
    });

    it("re-syncs from an externally-changed value prop", () => {
        const onChange = vi.fn();
        const { rerender } = render(
            withLanguage(
                <PhoneInput
                    id="phone"
                    label="Phone"
                    countrySelectLabel="Country code"
                    value="+5511987654321"
                    onChange={onChange}
                />,
            ),
        );

        expect(screen.getByLabelText("Phone")).toHaveValue("(11) 98765-4321");

        rerender(
            withLanguage(
                <PhoneInput
                    id="phone"
                    label="Phone"
                    countrySelectLabel="Country code"
                    value="+12025551234"
                    onChange={onChange}
                />,
            ),
        );

        expect(screen.getByLabelText("Phone")).toHaveValue("(202) 555-1234");
        expect(countryTrigger()).toHaveAccessibleName(/United States \(\+1\)/);
    });
});
