import { cloneElement, isValidElement, useId } from "react";
import type { ReactElement } from "react";

interface TooltipProps {
    text: string;
    children: ReactElement<{ "aria-describedby"?: string }>;
}

// Wraps a single trigger element (usually an icon-only button that already has its own
// aria-label) with a floating label shown on both mouse hover and keyboard focus, linked via
// aria-describedby for assistive technology.
export function Tooltip({ text, children }: TooltipProps) {
    const id = useId();
    const trigger = isValidElement(children)
        ? cloneElement(children, { "aria-describedby": id })
        : children;

    return (
        <span className="group relative inline-flex">
            {trigger}
            <span
                id={id}
                role="tooltip"
                className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-2 -translate-x-1/2 rounded bg-gray-900 px-2 py-1 text-xs whitespace-nowrap text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100"
            >
                {text}
            </span>
        </span>
    );
}
