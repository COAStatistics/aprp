import pytest

from tests.watchlists.factories import WatchlistFactory, WatchlistItemFactory


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
