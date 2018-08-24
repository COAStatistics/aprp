from rest_framework.serializers import ModelSerializer
from watchlists.models import Watchlist, WatchlistItem
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



