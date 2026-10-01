import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";

import { ChevronDownIcon } from "./icons.tsx";

interface DropdownProps {
    label: ReactNode;
    children: (close: () => void) => ReactNode;
    align?: "left" | "right";
}

export function Dropdown({ label, children, align = "left" }: DropdownProps) {
    const [open, setOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!open) {
            return;
        }

        const onPointerDown = (event: PointerEvent) => {
            if (
                containerRef.current &&
                !containerRef.current.contains(event.target as Node)
            ) {
                setOpen(false);
            }
        };
        const onKeyDown = (event: KeyboardEvent) => {
            if (event.key === "Escape") {
                setOpen(false);
            }
        };

        document.addEventListener("pointerdown", onPointerDown);
        document.addEventListener("keydown", onKeyDown);

        return () => {
            document.removeEventListener("pointerdown", onPointerDown);
            document.removeEventListener("keydown", onKeyDown);
        };
    }, [open]);

    return (
        <div ref={containerRef} className="relative">
            <button
                type="button"
                aria-expanded={open}
                aria-haspopup="menu"
                onClick={() => setOpen((current) => !current)}
                className="flex w-full items-center gap-1 rounded px-3 py-2 text-gray-300 hover:text-white"
            >
                {label}
                <ChevronDownIcon
                    className={`size-4 transition-transform ${open ? "rotate-180" : ""}`}
                />
            </button>

            {open && (
                <div
                    role="menu"
                    className={`z-20 mt-1 w-full overflow-hidden rounded-lg bg-white py-1 text-gray-800 shadow-lg ring-1 ring-black/5 md:absolute md:w-56 ${
                        align === "right" ? "md:right-0" : "md:left-0"
                    }`}
                >
                    {children(() => setOpen(false))}
                </div>
            )}
        </div>
    );
}
