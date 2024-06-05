import pytest
from django.contrib.auth.models import User

from apps.configs.models import Source, AbstractProduct
from apps.watchlists.models import Watchlist, WatchlistItem, MonitorProfile
from tests.watchlists.factories import WatchlistItemFactory, MonitorProfileFactory


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

    def test_watchlist_item_with_delete_case_cade(self, watchlist_item):
        watchlist_item.product.delete()

        with pytest.raises(Exception):
            AbstractProduct.objects.get(id=watchlist_item.product.id)
            WatchlistItem.objects.get(id=watchlist_item.id)

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

    def test_filter_by_product_method(self, watchlist_item):
        watchlist_items = WatchlistItem.objects.filter_by_product(product=watchlist_item.product)

        assert watchlist_items.count() == 1
        assert watchlist_items.first() == watchlist_item

        # Test with no product
        watchlist_items = WatchlistItem.objects.filter_by_product()

        assert watchlist_items.count() == 0


@pytest.mark.django_db
class TestMonitorProfileModel:
    def test_monitor_profile_instance(self, monitor_profile_with_pig):
        profile = monitor_profile_with_pig

        assert profile.product is not None
        assert profile.watchlist is not None
        assert profile.type is not None
        assert profile.price is not None
        assert profile.comparator is not None
        assert profile.color is not None
        assert profile.is_active is False
        assert profile.always_display is False
        assert profile.update_time is not None

    def test_monitor_profile_instance_with_null_values(self, product_of_pig):
        with pytest.raises(Exception):
            WatchlistItemFactory.create(product=None)

        with pytest.raises(Exception):
            WatchlistItemFactory.create(product=product_of_pig, watchlist=None)

    def test_monitor_profile_with_product(self, product_of_pig, watchlist):
        profile = MonitorProfileFactory(product=product_of_pig, watchlist=watchlist)
        product = profile.product

        # Check reverse relationship
        product_instance = AbstractProduct.objects.get(monitorprofile=profile)
        assert product_instance == product

        # Check reverse query
        profile_instance = MonitorProfile.objects.get(product=product)
        assert profile_instance.id == profile.id

    def test_monitor_profile_with_watchlist(self, product_of_pig, watchlist):
        profile = MonitorProfileFactory(product=product_of_pig, watchlist=watchlist)
        watchlist = profile.watchlist

        # Check reverse relationship
        watchlist_instance = Watchlist.objects.get(monitorprofile=profile)
        assert watchlist_instance == watchlist

        # Check reverse query
        profile_instance = MonitorProfile.objects.get(watchlist=watchlist)
        assert profile_instance.id == profile.id

    def test_monitor_profile_delete_with_product(self, monitor_profile_with_pig):
        profile = monitor_profile_with_pig
        profile.product.delete()

        with pytest.raises(Exception):
            AbstractProduct.objects.get(id=profile.product.id)
            MonitorProfile.objects.get(id=profile.id)

    def test_monitor_profile_delete_with_watchlist(self, monitor_profile_with_pig):
        profile = monitor_profile_with_pig
        profile.watchlist.delete()

        with pytest.raises(Exception):
            Watchlist.objects.get(id=profile.product.id)
            MonitorProfile.objects.get(id=profile.id)

    def test_monitor_profile_delete_with_type(self, monitor_profile_with_pig):
        profile = monitor_profile_with_pig
        profile.type.delete()

        with pytest.raises(Exception):
            Watchlist.objects.get(id=profile.product.id)

        profile = MonitorProfile.objects.get(id=profile.id)

        assert profile.type is None

    def test_str_method(self, monitor_profile_with_pig):
        profile = monitor_profile_with_pig
        product = profile.product
        watchlist = profile.watchlist
        assert str(profile) == f'product: {product.name}, watchlist: {watchlist.name}, price: {profile.price}'

    def test_sibling_method(self, monitor_profile_with_pig):
        profile = monitor_profile_with_pig

        assert profile.sibling().count() == 1
        assert profile.sibling().first() != profile

    def test_watchlist_items(self, monitor_profile_with_pig):
        profile = monitor_profile_with_pig

        assert profile.watchlist_items().count() == 0

    def test_product_list_method(self, monitor_profile_with_pig):
        # Act
        result = monitor_profile_with_pig.product_list()

        assert result is not None
        assert len(result) == 1
        assert result[0] == monitor_profile_with_pig.product

    def test_sources_method(self, monitor_profile_with_pig, watchlist_item_with_pig):
        # Act
        result = monitor_profile_with_pig.sources()

        # Assert
        assert result is not None
        assert len(result) == watchlist_item_with_pig.sources.count()

    def test_active_compare_method(self, monitor_profile_with_pig):
        # Act
        result = monitor_profile_with_pig.active_compare(79.0)

        # Assert
        assert result is False

        result = monitor_profile_with_pig.active_compare(78.0)
        assert result is True

    def test_format_price_method(self, monitor_profile_with_pig):
        # Act
        result = monitor_profile_with_pig.format_price

        # Assert
        assert result == '<79元/公斤'

    def test_price_range_method(self, monitor_profile_with_pig):
        # Act
        result = monitor_profile_with_pig.price_range

        # Assert
        assert result == [65.0, 79.0]
