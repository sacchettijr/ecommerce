from typing import TYPE_CHECKING

from factory.declarations import PostGenerationMethodCall
from factory.django import DjangoModelFactory
from factory.faker import Faker

from account.models import UserModel
from utils.env import env

if TYPE_CHECKING:
    BaseDjangoModelFactory = DjangoModelFactory[UserModel]
else:
    BaseDjangoModelFactory = DjangoModelFactory


class UserFactory(BaseDjangoModelFactory):
    name = Faker(
        provider="name",
        locale="pt-br",
    )
    email = Faker(provider="email")
    date_birth = Faker(
        provider="date_of_birth",
        minimum_age=18,
        maximum_age=90,
    )
    is_active = True
    is_email_verified = True
    password = PostGenerationMethodCall(
        "set_password",
        env(
            name="USER_TEST_PASSWORD",
        ),
    )

    class Meta:
        model = UserModel
        django_get_or_create = ("email",)
