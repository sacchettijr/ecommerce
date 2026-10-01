export function inputClassName(hasError: boolean): string {
    const base =
        "block w-full rounded-lg border bg-white px-3 py-2 text-gray-900 shadow-sm focus:outline-none focus:ring-2";

    return hasError
        ? `${base} border-red-500 focus:ring-red-300`
        : `${base} border-gray-300 focus:border-blue-500 focus:ring-blue-200`;
}
