window.ecommerce = window.ecommerce || {};

// Aproxima django.utils.text.slugify (a unicidade "-1", "-2" é resolvida só no servidor).
window.ecommerce.slugify = function (value) {
    if (!value) {
        return "";
    }

    return value
        .toString()
        .normalize("NFKD")
        .replace(/[^\x00-\x7F]/g, "")
        .toLowerCase()
        .replace(/[^\w\s-]/g, "")
        .replace(/[-\s]+/g, "-")
        .replace(/^[-_]+|[-_]+$/g, "");
};
