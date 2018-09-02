from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
)
from watchlists.models import (
    Watchlist,
    WatchlistItem,
    MonitorProfile,

)
from configs.api.serializers import SourceSerializer


class WatchlistItemSerializer(ModelSerializer):
    sources = SourceSerializer(many=True)

    class Meta:
        model = WatchlistItem
        fields = '__all__'


class WatchlistSerializer(ModelSerializer):
    children = WatchlistItemSerializer(many=True)

    class Meta:
        model = Watchlist
        fields = '__all__'


class MonitorProfileSerializer(ModelSerializer):
    format_price = SerializerMethodField()
    up_price = SerializerMethodField()
    low_price = SerializerMethodField()
    watchlist = SerializerMethodField()

    def get_format_price(self, obj):
        return obj.format_price

    def get_up_price(self, obj):
        return obj.up_price

    def get_low_price(self, obj):
        return obj.low_price

    def get_watchlist(self, obj):
        return obj.watchlist.name

    class Meta:
        model = MonitorProfile
        fields = ['format_price', 'low_price', 'up_price', 'type', 'color', 'watchlist']



