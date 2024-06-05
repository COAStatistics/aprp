import pytest

from tests.dailytrans.factories import (
    DailyTranFactory,
)


@pytest.fixture
def daily_tran(product_of_pig, sources_for_pig):
    return DailyTranFactory(
        product=product_of_pig,
        source=sources_for_pig[0],
    )
