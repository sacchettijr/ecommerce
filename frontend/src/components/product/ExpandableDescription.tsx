import { useId, useState } from "react";

import { useLanguage } from "../../i18n/useLanguage.ts";
import { Markdown } from "../ui/Markdown.tsx";

// Preview threshold: a plain character count on the raw markdown source,
// not a measured rendered height. Simpler, deterministic, and testable,
// at the cost of not accounting for how formatting (headings, lists)
// affects the actual rendered height for a given description.
const PREVIEW_THRESHOLD = 320;

export function ExpandableDescription({ description }: { description: string }) {
    const { t } = useLanguage();
    const [expanded, setExpanded] = useState(false);
    const contentId = useId();

    const needsToggle = description.length > PREVIEW_THRESHOLD;

    return (
        <div>
            <div
                id={contentId}
                className={
                    needsToggle && !expanded
                        ? "max-h-40 overflow-hidden"
                        : undefined
                }
            >
                <Markdown>{description}</Markdown>
            </div>

            {needsToggle && (
                <button
                    type="button"
                    aria-expanded={expanded}
                    aria-controls={contentId}
                    onClick={() => setExpanded((value) => !value)}
                    className="text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline"
                >
                    {expanded ? t.product.showLess : t.product.readMore}
                </button>
            )}
        </div>
    );
}
