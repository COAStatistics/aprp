import threading

import factory
from django.contrib.auth.models import User
from factory import Faker
from factory.django import DjangoModelFactory


class BaseFactory(DjangoModelFactory):
    class Meta:
        strategy = factory.CREATE_STRATEGY
        model = None
        abstract = True

    _SEQUENCE = 1
    _SEQUENCE_LOCK = threading.Lock()

    @classmethod
    def _setup_next_sequence(cls):
        with cls._SEQUENCE_LOCK:
            cls._SEQUENCE += 1
            return cls._SEQUENCE


class UserFactory(BaseFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    first_name = Faker('first_name', locale='zh_TW')
    last_name = Faker('last_name', locale='zh_TW')
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@domain.com")
    password = factory.PostGeneration(lambda obj, *args, **kwargs: obj.set_password(obj.username))
