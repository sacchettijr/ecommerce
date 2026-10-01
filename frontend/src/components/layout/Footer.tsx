import { company } from "../../config/company.ts";
import { useLanguage } from "../../i18n/useLanguage.ts";
import { EnvelopeIcon, PhoneIcon, WhatsAppIcon } from "../ui/icons.tsx";

const linkClassName = "text-gray-100 hover:underline";

export function Footer() {
    const { t } = useLanguage();

    return (
        <footer className="mt-16 bg-gray-900 py-8 text-gray-100">
            <div className="mx-auto grid max-w-7xl gap-6 px-4 md:grid-cols-3">
                <div>
                    <h6 className="mb-2 text-xs font-semibold uppercase text-gray-400">
                        {t.footer.address}
                    </h6>
                    <p className="text-sm">
                        {company.addressLine1}
                        <br />
                        {company.addressLine2}
                        <br />
                        {company.addressCep}
                    </p>
                </div>

                <div>
                    <h6 className="mb-2 text-xs font-semibold uppercase text-gray-400">
                        {t.footer.contact}
                    </h6>
                    <p className="mb-1 flex items-center gap-2 text-sm">
                        <PhoneIcon className="size-4" />
                        <a href={company.phoneHref} className={linkClassName}>
                            {company.phone}
                        </a>
                        <a
                            href={company.whatsappHref}
                            target="_blank"
                            rel="noopener noreferrer"
                            title={t.footer.whatsapp}
                            className={`${linkClassName} ml-2 flex items-center gap-1`}
                        >
                            <WhatsAppIcon className="size-4" />
                            {t.footer.whatsapp}
                        </a>
                    </p>
                    <p className="flex items-center gap-2 text-sm">
                        <EnvelopeIcon className="size-4" />
                        <a
                            href={`mailto:${company.email}`}
                            className={linkClassName}
                        >
                            {company.email}
                        </a>
                    </p>
                </div>

                <div className="md:text-right">
                    <p>
                        {company.name} © {new Date().getFullYear()}
                    </p>
                </div>
            </div>
        </footer>
    );
}
