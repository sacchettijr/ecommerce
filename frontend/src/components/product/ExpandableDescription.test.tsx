import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { renderWithProviders } from "../../test/renderWithProviders.tsx";
import { ExpandableDescription } from "./ExpandableDescription.tsx";

describe("ExpandableDescription", () => {
    it("renders a short description with no toggle control", () => {
        renderWithProviders(
            <ExpandableDescription description="A short description." />,
        );

        expect(screen.getByText("A short description.")).toBeInTheDocument();
        expect(
            screen.queryByRole("button", { name: "Read more" }),
        ).not.toBeInTheDocument();
    });

    it("shows a Read more control for a long description, collapsed by default", () => {
        const longDescription = "Lorem ipsum dolor sit amet. ".repeat(20);

        renderWithProviders(
            <ExpandableDescription description={longDescription} />,
        );

        const button = screen.getByRole("button", { name: "Read more" });
        expect(button).toHaveAttribute("aria-expanded", "false");
    });

    it("expands on click, revealing Show less, and collapses again on a second click", async () => {
        const longDescription = "Lorem ipsum dolor sit amet. ".repeat(20);
        const user = userEvent.setup();

        renderWithProviders(
            <ExpandableDescription description={longDescription} />,
        );

        await user.click(screen.getByRole("button", { name: "Read more" }));
        const expandedButton = screen.getByRole("button", {
            name: "Show less",
        });
        expect(expandedButton).toHaveAttribute("aria-expanded", "true");

        await user.click(expandedButton);
        expect(
            screen.getByRole("button", { name: "Read more" }),
        ).toHaveAttribute("aria-expanded", "false");
    });

    it("does not render a toggle for an empty description", () => {
        renderWithProviders(<ExpandableDescription description="" />);

        expect(
            screen.queryByRole("button", { name: "Read more" }),
        ).not.toBeInTheDocument();
    });
});
