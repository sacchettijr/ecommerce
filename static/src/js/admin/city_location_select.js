// Country -> State -> City cascading select fields for User Addresses.
//
// Two mechanisms work together:
//   1. Every <option> (whether rendered server-side by StateLocationSelect/
//      CityLocationSelect, or rebuilt here from a fetch) carries data-state/
//      data-country attributes. Picking a city or a state reads them straight
//      off the selected <option> to populate its parent field(s) - no request
//      needed for that direction.
//   2. Picking a country or a state narrows the *options* of its dependent
//      field(s) by fetching the admin-only /api/address/ endpoints and
//      rebuilding the <option> list, preserving a still-valid selection and
//      clearing one that's no longer compatible.
//
// No code path here ever dispatches a synthetic "change" event, so there is
// no event-loop risk to guard against - the only ordering hazard is two
// overlapping fetches for the same field resolving out of order, handled by
// the per-field request tokens below.
(function () {
    var stateListToken = 0;
    var cityListToken = 0;

    function fieldSelect(sourceName, fieldName) {
        return document.querySelector(
            '[name="' + sourceName.replace(/[a-z]+$/, fieldName) + '"]',
        );
    }

    function selectedOptionData(select, attr) {
        var option = select.options[select.selectedIndex];
        return option ? option.getAttribute(attr) : null;
    }

    // Rebuilds a <select>'s options from a list of {id, name, state?, country?}
    // rows (state rows carry country; city rows carry state and country).
    // Keeps the current selection if it's still present in the new list,
    // otherwise clears it. Returns whether the selection was kept.
    function rebuildOptions(select, rows) {
        var previousValue = select.value;
        var keep = false;

        while (select.firstChild) {
            select.removeChild(select.firstChild);
        }

        var placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = "---------";
        select.appendChild(placeholder);

        for (var i = 0; i < rows.length; i++) {
            var row = rows[i];
            var option = document.createElement("option");
            option.value = String(row.id);
            option.textContent = row.name;

            if (row.state !== undefined) {
                option.setAttribute("data-state", String(row.state));
            }
            if (row.country !== undefined) {
                option.setAttribute("data-country", String(row.country));
            }
            if (String(row.id) === previousValue) {
                keep = true;
            }

            select.appendChild(option);
        }

        select.value = keep ? previousValue : "";
        return keep;
    }

    function fetchCitiesForState(stateSelect) {
        var citySelect = fieldSelect(stateSelect.name, "city");

        if (!citySelect) {
            return;
        }

        if (!stateSelect.value) {
            rebuildOptions(citySelect, []);
            return;
        }

        var token = ++cityListToken;

        fetch("/api/address/cities/?state=" + encodeURIComponent(stateSelect.value))
            .then(function (response) {
                return response.json();
            })
            .then(function (cities) {
                if (token !== cityListToken) {
                    return; // A newer state/country selection has already started.
                }
                rebuildOptions(citySelect, cities);
            });
    }

    // Rebuilds the state dropdown's options to those of the given country.
    // `refreshCities` controls whether the city list is also refreshed once the
    // (possibly kept, possibly cleared) state value settles: the country-change
    // handler needs that (it doesn't know the resulting state value up front),
    // while the state-change handler already knows the exact target state and
    // refreshes cities for it immediately itself, without waiting on this fetch.
    function fetchStatesForCountry(countrySelect, refreshCities) {
        var stateSelect = fieldSelect(countrySelect.name, "state");

        if (!stateSelect) {
            return;
        }

        if (!countrySelect.value) {
            rebuildOptions(stateSelect, []);
            if (refreshCities) {
                fetchCitiesForState(stateSelect);
            }
            return;
        }

        var token = ++stateListToken;

        fetch("/api/address/states/?country=" + encodeURIComponent(countrySelect.value))
            .then(function (response) {
                return response.json();
            })
            .then(function (states) {
                if (token !== stateListToken) {
                    return; // A newer country selection has already started.
                }

                rebuildOptions(stateSelect, states);

                if (refreshCities) {
                    fetchCitiesForState(stateSelect);
                }
            });
    }

    // City chosen: its own <option> already carries data-state/data-country
    // (server-rendered via CityLocationSelect, or rebuilt by fetchCitiesForState
    // above, which now stamps the same attributes) - just read and apply them.
    document.addEventListener("change", function (event) {
        var citySelect = event.target;

        if (!citySelect || citySelect.tagName !== "SELECT" || !/-?city$/.test(citySelect.name)) {
            return;
        }

        var stateId = selectedOptionData(citySelect, "data-state");
        var countryId = selectedOptionData(citySelect, "data-country");

        if (!stateId || !countryId) {
            return;
        }

        var stateSelect = fieldSelect(citySelect.name, "state");
        var countrySelect = fieldSelect(citySelect.name, "country");

        if (stateSelect) {
            stateSelect.value = stateId;
        }
        if (countrySelect) {
            countrySelect.value = countryId;
        }
    });

    // State chosen directly: populate its country from the selected option's own
    // data-country, narrow the state dropdown's options to that country (cosmetic
    // - the chosen state's value itself never changes here), and refresh the
    // city list for the state that was actually picked - done immediately, not
    // waiting on the state-list fetch, since the target state is already known.
    document.addEventListener("change", function (event) {
        var stateSelect = event.target;

        if (
            !stateSelect ||
            stateSelect.tagName !== "SELECT" ||
            !/-?state$/.test(stateSelect.name)
        ) {
            return;
        }

        var countrySelect = fieldSelect(stateSelect.name, "country");
        var countryId = selectedOptionData(stateSelect, "data-country");

        if (countrySelect && countryId) {
            countrySelect.value = countryId;
            fetchStatesForCountry(countrySelect, /* refreshCities */ false);
        }

        fetchCitiesForState(stateSelect);
    });

    // Country chosen: narrow the state list, clearing state/city if they're no
    // longer compatible (fetchStatesForCountry itself refreshes cities once the
    // state list settles, since the resulting state value isn't known up front).
    document.addEventListener("change", function (event) {
        var countrySelect = event.target;

        if (
            !countrySelect ||
            countrySelect.tagName !== "SELECT" ||
            !/-?country$/.test(countrySelect.name)
        ) {
            return;
        }

        fetchStatesForCountry(countrySelect, /* refreshCities */ true);
    });
})();
