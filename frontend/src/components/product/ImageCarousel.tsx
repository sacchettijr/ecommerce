import { useState } from "react";

import type { ProductImage } from "../../api/types.ts";
import { useLanguage } from "../../i18n/useLanguage.ts";
import { ChevronLeftIcon, ChevronRightIcon } from "../ui/icons.tsx";

interface ImageCarouselProps {
    images: ProductImage[];
    name: string;
}

const controlClassName =
    "absolute inset-y-0 flex w-14 items-center justify-center text-white";

// A altura vem da proporção (com teto), nunca do conteúdo da coluna ao lado.
const frameClassName =
    "relative flex aspect-square max-h-[32rem] w-full items-center justify-center overflow-hidden rounded-lg p-6";

export function ImageCarousel({ images, name }: ImageCarouselProps) {
    const { t } = useLanguage();
    const [failed, setFailed] = useState<ReadonlySet<number>>(new Set());
    const [index, setIndex] = useState(0);

    // Imagens que não carregam saem do carousel; sem nenhuma restante, mostra a mensagem.
    const visible = images.filter((item) => !failed.has(item.id));

    if (visible.length === 0) {
        return (
            <div className={`${frameClassName} bg-gray-100 text-gray-500`}>
                {t.product.noProductImage}
            </div>
        );
    }

    const currentIndex = Math.min(index, visible.length - 1);
    const current = visible[currentIndex];
    const hasMany = visible.length > 1;

    const goTo = (target: number) =>
        setIndex((target + visible.length) % visible.length);

    const markFailed = (id: number) =>
        setFailed((previous) => new Set(previous).add(id));

    return (
        <div
            aria-roledescription="carousel"
            aria-label={name}
            className={`${frameClassName} bg-white ring-1 ring-gray-200`}
        >
            <img
                key={current.id}
                src={current.image}
                alt={t.product.imageAlt(name, currentIndex + 1)}
                onError={() => markFailed(current.id)}
                className="max-h-full max-w-full object-contain"
            />

            {hasMany && (
                <>
                    <button
                        type="button"
                        onClick={() => goTo(currentIndex - 1)}
                        className={`${controlClassName} left-0`}
                    >
                        <span className="rounded-full bg-black/40 p-2 hover:bg-black/60">
                            <ChevronLeftIcon className="size-6" />
                        </span>
                        <span className="sr-only">{t.pagination.previous}</span>
                    </button>
                    <button
                        type="button"
                        onClick={() => goTo(currentIndex + 1)}
                        className={`${controlClassName} right-0`}
                    >
                        <span className="rounded-full bg-black/40 p-2 hover:bg-black/60">
                            <ChevronRightIcon className="size-6" />
                        </span>
                        <span className="sr-only">{t.pagination.next}</span>
                    </button>

                    <div className="absolute inset-x-0 bottom-3 flex justify-center">
                        <div className="flex gap-2">
                            {visible.map((item, position) => (
                                <button
                                    key={item.id}
                                    type="button"
                                    onClick={() => goTo(position)}
                                    aria-label={t.product.slideLabel(
                                        position + 1,
                                    )}
                                    aria-current={position === currentIndex}
                                    className={`h-1 w-8 rounded-full ${
                                        position === currentIndex
                                            ? "bg-gray-800"
                                            : "bg-gray-300 hover:bg-gray-400"
                                    }`}
                                />
                            ))}
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
