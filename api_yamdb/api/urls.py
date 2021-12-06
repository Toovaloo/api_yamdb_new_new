from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitlesViewSet, UserViewSet,
                    get_confirmation_email, get_jwt_token)

router_v1 = DefaultRouter()
router_v1.register('genres', GenreViewSet, basename='Genre')
router_v1.register('categories', CategoryViewSet, basename='Category')
router_v1.register('titles', TitlesViewSet, basename='Title')
router_v1.register('reviews', ReviewViewSet, basename='title_id')
router_v1.register('comments', CommentViewSet, basename='review_id')
router_v1.register('users', UserViewSet, basename='User')


urlpatterns = [
    path('v1/auth/email/', get_confirmation_email),
    path('v1/auth/token/', get_jwt_token),
    path('v1/', include(router_v1.urls)),
    path('v1/titles/<int:title_id>/', include(router_v1.urls)),
    path(
        'v1/titles/<int:title_id>/reviews/<int:review_id>/',
        include(router_v1.urls)
    ),
]
