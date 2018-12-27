from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
)
from watchlists.models import (
    Watchlist,
    WatchlistItem,
    MonitorProfile,
)
from dailytrans.utils import to_unix
from configs.api.serializers import SourceSerializer


class WatchlistItemSerializer(ModelSerializer):
    sources = SourceSerializer(many=True)

    class Meta:
        model = WatchlistItem
        fields = '__all__'


class WatchlistSerializer(ModelSerializer):
    start_date = SerializerMethodField()
    end_date = SerializerMethodField()

    def get_start_date(self, obj):
        return to_unix(obj.start_date)

    def get_end_date(self, obj):
        return to_unix(obj.end_date)

    class Meta:
        model = Watchlist
        fields = ['name', 'start_date', 'end_date']


class MonitorProfileSerializer(ModelSerializer):
    format_price = SerializerMethodField()
    up_price = SerializerMethodField()
    low_price = SerializerMethodField()
    watchlist = SerializerMethodField()
    start_date = SerializerMethodField()
    end_date = SerializerMethodField()

    def get_format_price(self, obj):
        return obj.format_price

    def get_up_price(self, obj):
        return obj.up_price

    def get_low_price(self, obj):
        return obj.low_price

    def get_watchlist(self, obj):
        return obj.watchlist.name

    def get_start_date(self, obj):
        return to_unix(obj.watchlist.start_date)

    def get_end_date(self, obj):
        return to_unix(obj.watchlist.end_date)

    class Meta:
        model = MonitorProfile
        fields = ['format_price', 'low_price', 'up_price', 'type', 'color', 'watchlist', 'start_date', 'end_date']
