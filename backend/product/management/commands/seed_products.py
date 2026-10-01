import random
from typing import (
    Any,
)

from django.core.management import (
    BaseCommand,
    CommandParser,
)

from product.tests.factories import (
    ProductCategoryFactory,
    ProductFactory,
    ProductImageFactory,
)


class Command(BaseCommand):
    help = (
        "Create fake products with images (by ProductFactory/ProductImageFactory) "
        "for development/demonstration."
    )

    def add_arguments(
        self,
        parser: CommandParser,
    ) -> None:

        parser.add_argument(
            "--amount",
            type=int,
            default=50,
            help="Number of products to create (default: 50).",
        )

        parser.add_argument(
            "--categories",
            type=int,
            default=8,
            help="Number of categories to create e distribute amongproducts (default: 8).",
        )

        return super().add_arguments(parser)

    def handle(
        self,
        *args: Any,
        **options: Any,
    ) -> None:

        amount: int = options["amount"]
        categories_amount: int = options["categories"]

        categories = [ProductCategoryFactory() for _ in range(categories_amount)]

        for _ in range(amount):
            product = ProductFactory(
                category=random.choice(
                    seq=categories,
                ),
            )

            for order in range(random.randint(a=1, b=3)):
                ProductImageFactory(
                    product=product,
                    is_primary=(order == 0),
                    order=order,
                )

        self.stdout.write(
            msg=self.style.SUCCESS(
                text=(
                    f"{amount} products created with images distributed across "
                    f"{categories_amount} categories."
                )
            ),
        )
