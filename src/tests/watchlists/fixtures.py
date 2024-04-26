import pytest

from tests.configs.factories import TypeFactory, ConfigFactory, UnitFactory, AbstractProductFactory
from tests.watchlists.factories import WatchlistFactory, WatchlistItemFactory, MonitorProfileFactory


@pytest.fixture
def watchlist(user_with_admin):
    return WatchlistFactory(
        name="113上半年",
        user=user_with_admin,
    )


@pytest.fixture
def watchlist_item(watchlist, product_of_rice, source):
    return WatchlistItemFactory(
        product=product_of_rice,
        sources=[source],
        parent=watchlist,
    )


@pytest.fixture
def watchlist_item_with_sources(product_of_rice, sources):
    return WatchlistItemFactory(
        product=product_of_rice,
        sources=sources,
    )


@pytest.fixture
def type_for_pig():
    return TypeFactory(name="批發")


@pytest.fixture
def config_for_pig():
    return ConfigFactory(
        name="毛豬",
        code="COG08",
        type_level=1,
    )


@pytest.fixture
def unit_for_pig():
    return UnitFactory(
        price_unit="元/公斤",
        volume_unit="頭",
        weight_unit="公斤",
    )


@pytest.fixture
def product_of_pig(config_for_pig, type_for_pig, unit_for_pig):
    return AbstractProductFactory(
        name="規格豬",
        code="規格豬(65公斤以上)",
        track_item=True,
        config=config_for_pig,
        type=type_for_pig,
        unit=unit_for_pig,
    )


@pytest.fixture
def monitor_profile_with_pig(product_of_pig, watchlist):
    MonitorProfileFactory(
        product=product_of_pig,
        watchlist=watchlist,
        type=product_of_pig.type,
        price=65.0,
    )

    return MonitorProfileFactory(
        product=product_of_pig,
        watchlist=watchlist,
        type=product_of_pig.type,
        price=79.0,
    )
