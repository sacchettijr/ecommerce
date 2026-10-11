---
description: Identify missing test coverage, create or update tests, and run relevant checks when authorized
---

Work on test coverage for: $ARGUMENTS

If no specific target is given, consult `.claude/context/testing.md` for
known gaps — `address/` and `core/` currently have zero tests, and several
specific models/forms/viewsets in `account/`/`product/` are listed there
as uncovered.

Steps:

1. Confirm the current coverage gap by reading the actual code and the
   app's `tests/` directory — `.claude/context/testing.md` is a snapshot,
   not guaranteed current.
2. If the target app has no factories yet (`address`/`core` do not),
   write them first, following the existing pattern in
   `account/tests/factories/` or `product/tests/factories/`
   (`TYPE_CHECKING`-guarded `DjangoModelFactory[Model]`, `Faker`/
   `SubFactory` usage).
3. Write function-based pytest tests, `pytestmark =
   pytest.mark.django_db`, matching the app's `tests/{api,models,views}/`
   layout — do not place a new test file directly under `tests/` the way
   `account/tests/test_frontend_url.py` currently does.
4. Cover: normal behavior, invalid input, boundary conditions, relevant
   database constraints (e.g. the `UniqueConstraint`s on
   `ProductImageModel`/`UserAddressModel`), and — for anything touching
   Celery — that dispatch failures are handled the way
   `utils/dispatch_task.py` intends (logged and swallowed, not
   propagated).
5. Do not create superficial tests merely to raise a count — each test
   should assert something that could actually fail.
6. Run the new tests and the full suite afterward; report actual
   pass/fail, not an assumption.
7. Update `.claude/context/testing.md`'s coverage table if this closes a
   gap it lists.
