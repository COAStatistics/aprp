from django.db.models import Q

from rest_framework.filters import (
        SearchFilter,
        OrderingFilter,
)
from rest_framework.generics import (
    ListAPIView,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    )
from posts.models import Post
from .pagination import (
    PostLimitOffsetPagination,
    PostPageNumberPagination
)
from .serializers import (
    PostListSerializer
)


class PostListAPIView(ListAPIView):
    serializer_class = PostListSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated]
    search_fields = ['title', 'content', 'user__username']
    pagination_class = PostPageNumberPagination #PageNumberPagination

    def get_queryset(self, *args, **kwargs):
        queryset_list = Post.objects.all()
        query = self.request.GET.get("q")
        count =self.request.GET.get("count")
        start = self.request.GET.GET("start")

        if query:
            queryset_list = queryset_list.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(user__first_name__icontains=query) |
                    Q(user__last_name__icontains=query) |
                    Q(user__username__icontains=query)
            ).distinct()

        if start:
            queryset_list = queryset_list[start:]

        if count:
            queryset_list = queryset_list[:count]

        return queryset_list
