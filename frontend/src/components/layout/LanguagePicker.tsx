import { useLanguage } from "../../i18n/useLanguage.ts";
import { Dropdown } from "../ui/Dropdown.tsx";

export function LanguagePicker() {
    const { language, setLanguage, languages, t } = useLanguage();
    const current = languages.find((item) => item.code === language);

    return (
        <Dropdown
            align="right"
            label={
                current && (
                    <img
                        src={current.flag}
                        alt={current.nativeName}
                        width={20}
                        height={20}
                        className="rounded-sm"
                    />
                )
            }
        >
            {(close) => (
                <>
                    <p className="px-4 py-2 text-xs font-semibold uppercase text-gray-500">
                        {t.nav.language}
                    </p>
                    {languages.map((item) => (
                        <button
                            key={item.code}
                            type="button"
                            role="menuitem"
                            onClick={() => {
                                setLanguage(item.code);
                                close();
                            }}
                            aria-current={item.code === language}
                            className={`flex w-full items-center gap-2 px-4 py-2 text-left hover:bg-gray-100 ${
                                item.code === language
                                    ? "font-semibold text-blue-600"
                                    : ""
                            }`}
                        >
                            <img
                                src={item.flag}
                                alt=""
                                width={20}
                                height={20}
                                className="rounded-sm"
                            />
                            {item.nativeName}
                        </button>
                    ))}
                </>
            )}
        </Dropdown>
    );
}
