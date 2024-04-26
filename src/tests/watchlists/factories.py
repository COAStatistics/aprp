import factory
from factory import Faker, SubFactory

from apps.watchlists.models import Watchlist, WatchlistItem, MonitorProfile
from tests.configs.factories import SourceFactory, AbstractProductFactory, TypeFactory
from tests.factories import BaseFactory


class WatchlistFactory(BaseFactory):
    class Meta:
        model = Watchlist

    name = Faker('name', 'zh_TW')
    user = SubFactory('tests.factories.UserFactory')


class WatchlistItemFactory(BaseFactory):
    class Meta:
        model = WatchlistItem

    product = SubFactory(AbstractProductFactory)
    parent = SubFactory(WatchlistFactory)

    @factory.post_generation
    def sources(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for source in extracted:
                self.sources.add(source)


class MonitorProfileFactory(BaseFactory):

    class Meta:
        model = MonitorProfile

    product = SubFactory(AbstractProductFactory)
    watchlist = SubFactory(WatchlistFactory)
    type = SubFactory(TypeFactory)
    price = Faker('pyfloat')

    @factory.post_generation
    def months(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for month in extracted:
                self.months.add(month)
