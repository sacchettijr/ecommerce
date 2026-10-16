document.addEventListener("DOMContentLoaded", function () {
    var group = document.getElementById("images-group");

    if (!group) {
        return;
    }

    // Only one primary image at a time within this product's inline formset:
    // checking one unchecks every other primary checkbox in the same group.
    group.addEventListener("change", function (event) {
        var target = event.target;

        if (!target.matches('input[name$="-is_primary"]') || !target.checked) {
            return;
        }

        var checkboxes = group.querySelectorAll('input[name$="-is_primary"]');
        for (var i = 0; i < checkboxes.length; i++) {
            if (checkboxes[i] !== target) {
                checkboxes[i].checked = false;
            }
        }
    });

    // New inline row: pre-fill its order field with the next position after the
    // current maximum among visible, not-yet-deleted rows (not a row count, so it
    // stays correct even if the formset currently has gaps).
    document.addEventListener("formset:added", function (event) {
        if (event.detail.formsetName !== "images") {
            return;
        }

        var newRow = event.target;
        var newOrderInput = newRow.querySelector('input[name$="-order"]');

        if (!newOrderInput) {
            return;
        }

        var orderInputs = group.querySelectorAll('input[name$="-order"]');
        var maxOrder = -1;

        for (var i = 0; i < orderInputs.length; i++) {
            var orderInput = orderInputs[i];

            if (orderInput === newOrderInput) {
                continue;
            }

            //   ".form-row" (not ".dynamic-images", which Django's inlines.js only adds
            //   to rows cloned via "Add another") is present on every row - existing,
            //   already-saved ones included - so an existing row marked for deletion is
            //   correctly excluded too, not just a newly-added one.
            var row = orderInput.closest(".form-row");
            var deleteCheckbox = row
                ? row.querySelector('input[name$="-DELETE"]')
                : null;

            if (deleteCheckbox && deleteCheckbox.checked) {
                continue;
            }

            var value = parseInt(orderInput.value, 10);
            if (!isNaN(value) && value > maxOrder) {
                maxOrder = value;
            }
        }

        newOrderInput.value = String(maxOrder + 1);
    });
});
