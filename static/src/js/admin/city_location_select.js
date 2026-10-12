document.addEventListener("change", function (event) {
    var citySelect = event.target;

    if (!citySelect || citySelect.tagName !== "SELECT" || !/-?city$/.test(citySelect.name)) {
        return;
    }

    var option = citySelect.options[citySelect.selectedIndex];
    var stateId = option ? option.getAttribute("data-state") : null;
    var countryId = option ? option.getAttribute("data-country") : null;

    if (!stateId || !countryId) {
        return;
    }

    var stateSelect = document.querySelector(
        '[name="' + citySelect.name.replace(/city$/, "state") + '"]',
    );
    var countrySelect = document.querySelector(
        '[name="' + citySelect.name.replace(/city$/, "country") + '"]',
    );

    if (stateSelect) {
        stateSelect.value = stateId;
    }

    if (countrySelect) {
        countrySelect.value = countryId;
    }
});
