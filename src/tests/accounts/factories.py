from django.contrib.auth.models import Group
from factory import Faker, SubFactory

from apps.accounts.models import GroupInformation
from tests.factories import BaseFactory


class GroupFactory(BaseFactory):
    class Meta:
        model = Group

    name = Faker('word', 'zh_TW')


class GroupInformationFactory(BaseFactory):
    class Meta:
        model = GroupInformation

    name = Faker('word', 'zh_TW')
    group = SubFactory(GroupFactory)
    email_dns = Faker('free_email_domain')
