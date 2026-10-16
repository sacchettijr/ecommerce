document.addEventListener("DOMContentLoaded", function () {
    var group = document.getElementById("user_addresses-group");

    if (!group) {
        return;
    }

    // Only one primary address at a time within this user's inline formset:
    // checking one unchecks every other primary checkbox in the same group.
    // Scoped to this group (not document), so it can never reach another
    // user's addresses - each User admin page only ever renders one user's
    // inline anyway, but the scoping documents that intent explicitly.
    group.addEventListener("change", function (event) {
        var target = event.target;

        if (!target.matches('input[name$="-primary"]') || !target.checked) {
            return;
        }

        var checkboxes = group.querySelectorAll('input[name$="-primary"]');
        for (var i = 0; i < checkboxes.length; i++) {
            if (checkboxes[i] !== target) {
                checkboxes[i].checked = false;
            }
        }
    });
});
