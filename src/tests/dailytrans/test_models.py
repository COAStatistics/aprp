import datetime as dt
from datetime import datetime

import pytest

from apps.configs.models import AbstractProduct, Source
from apps.dailytrans.models import DailyTran
from tests.dailytrans.factories import (
    DailyTranFactory,
)


@pytest.mark.django_db
class TestDailyTranModel:
    def test_daily_tran_instance(self, daily_tran):
        assert daily_tran.product is not None
        assert daily_tran.source is not None
        assert daily_tran.up_price is not None
        assert daily_tran.mid_price is not None
        assert daily_tran.low_price is not None
        assert daily_tran.update_time is not None
        assert daily_tran.not_updated == 0
        assert daily_tran.create_time is not None

    def test_daily_tran_instance_with_null_product(self):
        with pytest.raises(Exception):
            DailyTranFactory.create(product=None)

    def test_daily_tran_instance_with_delete_case_cade_for_product(self, daily_tran):
        daily_tran.product.delete()

        with pytest.raises(Exception):
            AbstractProduct.objects.get(id=daily_tran.product.id)
            DailyTran.objects.get(id=daily_tran.id)

    def test_daily_tran_instance_with_delete_case_cade_for_source(self, daily_tran):
        daily_tran.source.delete()

        with pytest.raises(Exception):
            Source.objects.get(id=daily_tran.source.id)
            DailyTran.objects.get(id=daily_tran.id)

    def test_month_day_method(self, daily_tran):
        assert daily_tran.month_day == int(datetime.now().strftime('%m%d'))

    def test_between_month_day_filter_method_of_query_set(self, daily_tran):
        assert DailyTran.objects.between_month_day_filter() is not None
        assert DailyTran.objects.between_month_day_filter().count() == 1
        assert DailyTran.objects.between_month_day_filter().first() == daily_tran

        # Arrange
        date = datetime.now()

        # Act
        result = DailyTran.objects.between_month_day_filter(start_date=date, end_date=date)

        assert result is not None
        assert result.count() == 1
        assert result.first() == daily_tran

        # Arrange
        date = dt.date(year=2023, month=1, day=1)

        # Act
        result = DailyTran.objects.between_month_day_filter(start_date=date, end_date=date)

        assert result.count() == 0
