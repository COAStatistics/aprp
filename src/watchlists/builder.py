from django.contrib.auth.models import User
from .models import (
    Watchlist, WatchlistItem
)
from django.utils.translation import ugettext_lazy as _
from configs.models import AbstractProduct


def build_all():
    """
    create or update a watchlist with watch_all = True and related to all tracked product, sources
    """
    name = _('All')

    # user = User.objects.filter(is_superuser=True).first()
    # watchlist, created = Watchlist.objects.update_or_create(
    #     watch_all=True, name=name, user=user
    # )

    watchlist, created = Watchlist.objects.update_or_create(id=1)

    # if first build, remove all children and rebuild
    if not created:
        WatchlistItem.objects.filter(parent=watchlist).all().delete()

    track_items = AbstractProduct.objects.filter(track_item=True)

    for product in track_items:

        # seafood origin products which track_item is true not represent it is watchable, need to check its children
        """
        [<Seafood: 0.6-0.8公斤/尾>, <Seafood: 0.4公斤/尾>, <Seafood: 0.6公斤/尾>]
        [<Seafood: 800g以上>, <Seafood: 600g以下>, <Seafood: 600-800g>]
        [<Seafood: 1200g以上>, <Seafood: 1000g以下>, <Seafood: 1000-1200g>]
        [<Seafood: 3尾/公斤>, <Seafood: 5尾/公斤>, <Seafood: 4尾/公斤>]
        [<Seafood: 0.6-0.8公斤/尾>]
        [<Seafood: 0.6公斤/尾>, <Seafood: 0.45以下公斤/尾>, <Seafood: 0.45-0.6公斤/尾>]
        [<Seafood: 0.9公斤以上/尾>, <Seafood: 0.6公斤/尾>, <Seafood: 0.6-0.9公斤/尾>]
        [<Seafood: 1公斤>]
        [<Seafood: 35-40粒/0.6公斤>, <Seafood: 70-90粒/0.6公斤>, <Seafood: 40-60粒/0.6公斤>]
        [<Seafood: 800g以上>, <Seafood: 600g以下>, <Seafood: 600-800g>]
        [<Seafood: 600-800g>]
        [<Seafood: 600-800g>, <Seafood: 600g>]
        [<Seafood: 800g>]
        [<Seafood: 0.6公斤/尾>, <Seafood: 0.45以下公斤/尾>, <Seafood: 0.45-0.6公斤/尾>]
        [<Seafood: 40尾/0.6公斤>, <Seafood: 50尾/0.6公斤>]
        [<Seafood: 30台斤以上/尾>, <Seafood: 10-20台斤/尾>, <Seafood: 20-30台斤/尾>]
        """
        if product.has_child:

            for child in product.children():

                watchlist_item = WatchlistItem.objects.create(product=child, parent=watchlist)
                for source in child.sources():
                    watchlist_item.sources.add(source)

        else:

            watchlist_item = WatchlistItem.objects.create(product=product, parent=watchlist)
            for source in product.sources():
                watchlist_item.sources.add(source)



