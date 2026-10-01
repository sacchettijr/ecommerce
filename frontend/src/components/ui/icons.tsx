import type { SVGProps } from "react";

function Icon({
    shapes,
    ...props
}: SVGProps<SVGSVGElement> & { shapes: string | string[] }) {
    const paths = Array.isArray(shapes) ? shapes : [shapes];

    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.5}
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
            {...props}
        >
            {paths.map((item) => (
                <path key={item} d={item} />
            ))}
        </svg>
    );
}

export function CartPlusIcon(props: SVGProps<SVGSVGElement>) {
    return (
        <Icon
            shapes="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 0 0-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 0 0-16.536-1.84M7.5 14.25 5.106 5.272M6 20.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Zm12.75 0a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Z"
            {...props}
        />
    );
}

export function PhoneIcon(props: SVGProps<SVGSVGElement>) {
    return (
        <Icon
            shapes="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 0 0 2.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 0 1-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 0 0-1.091-.852H4.5A2.25 2.25 0 0 0 2.25 4.5v2.25Z"
            {...props}
        />
    );
}

export function EnvelopeIcon(props: SVGProps<SVGSVGElement>) {
    return (
        <Icon
            shapes="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75"
            {...props}
        />
    );
}

export function MapPinIcon(props: SVGProps<SVGSVGElement>) {
    return (
        <Icon
            shapes={[
                "M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z",
                "M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z",
            ]}
            {...props}
        />
    );
}

export function ChatIcon(props: SVGProps<SVGSVGElement>) {
    return (
        <Icon
            shapes="M2.25 12.76c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 0 1 1.037-.443 48.282 48.282 0 0 0 5.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z"
            {...props}
        />
    );
}

export function WhatsAppIcon(props: SVGProps<SVGSVGElement>) {
    return (
        <Icon
            shapes="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347zm-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884zm8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413"
            fill="currentColor"
            stroke="none"
            {...props}
        />
    );
}

export function MenuIcon(props: SVGProps<SVGSVGElement>) {
    return (
        <Icon
            shapes="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
            {...props}
        />
    );
}

export function CloseIcon(props: SVGProps<SVGSVGElement>) {
    return <Icon shapes="M6 18 18 6M6 6l12 12" {...props} />;
}

export function ChevronDownIcon(props: SVGProps<SVGSVGElement>) {
    return <Icon shapes="m19.5 8.25-7.5 7.5-7.5-7.5" {...props} />;
}

export function ChevronLeftIcon(props: SVGProps<SVGSVGElement>) {
    return <Icon shapes="M15.75 19.5 8.25 12l7.5-7.5" {...props} />;
}

export function ChevronRightIcon(props: SVGProps<SVGSVGElement>) {
    return <Icon shapes="m8.25 4.5 7.5 7.5-7.5 7.5" {...props} />;
}

export function HeartIcon(props: SVGProps<SVGSVGElement>) {
    return (
        <Icon
            shapes="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z"
            {...props}
        />
    );
}
