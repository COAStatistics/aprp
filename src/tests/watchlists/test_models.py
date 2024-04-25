import pytest
from django.contrib.auth.models import User

from apps.configs.models import Source
from apps.watchlists.models import Watchlist, WatchlistItem
from tests.watchlists.factories import WatchlistItemFactory


@pytest.mark.django_db
class TestWatchListModel:
    def test_watchlist_instance(self, watchlist):
        assert watchlist.name is not None
        assert watchlist.user is not None
        assert watchlist.is_default is False
        assert watchlist.watch_all is False
        assert watchlist.start_date is not None
        assert watchlist.end_date is not None
        assert watchlist.create_time is not None
        assert watchlist.update_time is not None

        # testing relationship
        user = User.objects.get(username=watchlist.user.username)

        assert user is not None

        # testing reverse relationship
        watchlist_instance = user.watchlist_set.all().first()

        assert watchlist == watchlist_instance

        # testing delete cascade
        user.delete()

        with pytest.raises(Exception):
            User.objects.get(id=watchlist.name.id)

        watchlist_instance = Watchlist.objects.get(id=watchlist.id)
        assert watchlist_instance.user is None

    def test_festival_str(self, watchlist):
        assert str(watchlist) == watchlist.name


@pytest.mark.django_db
class TestWatchlistItemModel:
    def test_watchlist_item(self, watchlist_item):
        assert watchlist_item.product is not None
        assert watchlist_item.sources is not None
        assert watchlist_item.parent is not None
        assert watchlist_item.update_time is not None

    def test_watchlist_item_with_null_product(self):
        with pytest.raises(Exception):
            WatchlistItemFactory.create(product=None)

    def test_watchlist_item_with_sources(self, watchlist_item_with_sources):
        sources = list(watchlist_item_with_sources.sources.all())

        assert watchlist_item_with_sources.sources.count() == len(sources)

        # Remove the source from the watchlist item
        source = sources.pop()
        watchlist_item_with_sources.sources.remove(source)
        assert watchlist_item_with_sources.sources.count() == len(sources)

        # Check reverse relationship
        filtered_sources = Source.objects.filter(watchlistitem__id=watchlist_item_with_sources.id)
        assert filtered_sources.count() == len(sources)

        # Check filter condition
        source = sources.pop()
        filtered_sources = Source.objects.filter(watchlistitem__id=watchlist_item_with_sources.id, name=source.name)
        assert filtered_sources.count() == len(sources)

        # Check reverse query
        watchlist_item_instance = WatchlistItem.objects.get(id=source.watchlistitem_set.first().id)
        sources = watchlist_item_instance.sources.all()
        assert sources.count() == len(sources)

        # Check get watchlist item instance by source name
        watchlist_item_instance = WatchlistItem.objects.filter(sources__name=source.name)
        assert watchlist_item_instance.count() == 1

    def test_watchlist_item_with_parent(self, watchlist_item):
        watchlist = Watchlist.objects.get(name=watchlist_item.parent.name)
        watchlist_item_instance = WatchlistItem.objects.select_related('parent').get(id=watchlist_item.id)

        assert watchlist_item_instance.parent is not None
        assert watchlist_item_instance.parent.name == watchlist.name
