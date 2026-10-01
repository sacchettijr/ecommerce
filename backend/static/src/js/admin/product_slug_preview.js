document.addEventListener("DOMContentLoaded", function () {
    var nameInput = document.getElementById("id_name");
    var slugPreview = document.querySelector(".field-slug .readonly");

    if (!nameInput || !slugPreview || !window.ecommerce) {
        return;
    }

    nameInput.addEventListener("input", function () {
        slugPreview.textContent =
            window.ecommerce.slugify(nameInput.value) || "-";
    });
});
