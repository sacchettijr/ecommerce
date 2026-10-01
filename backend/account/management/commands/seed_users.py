from typing import (
    Any,
)

from django.core.management import (
    BaseCommand,
    CommandParser,
)

from account.tests.factories import UserFactory


class Command(BaseCommand):
    help = "Create fake users (from UserFactory) for development/demonstration purposes."

    def add_arguments(
        self,
        parser: CommandParser,
    ) -> None:
        parser.add_argument(
            "--amount",
            type=int,
            default=50,
            help="Number of users to create (default=50).",
        )

    def handle(
        self,
        *args: Any,
        **options: Any,
    ) -> None:
        amount: int = options["amount"]

        users = [UserFactory() for _ in range(amount)]

        self.stdout.write(
            msg=self.style.SUCCESS(
                text=f"{len(users)} users created.",
            ),
        )
