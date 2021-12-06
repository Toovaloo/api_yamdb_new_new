from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFilter
from .models import Category, Comment, Genre, Review, Title
from .permissions import (IsAdminOrReadOnly, IsAuthorOrStaffOrReadOnly,
                          IsRoleAdminOrSuperuser,
                          IsRoleAdminOrSuperuserOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleCreateSerializer, TitleListSerializer,
                          UserSerializer)

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def get_confirmation_email(request):
    email = request.data.get('email')
    if email is None:
        return Response(request.data, status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(User, email=email)
    token = default_token_generator.make_token(user)
    send_mail(
        'confirmation_code',
        f'Ваш код подтверждения: {token}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    return Response(request.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    try:
        email = request.data.get('email')
        code = request.data.get('confirmation_code')
    except Exception:
        return Response(request.data, status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(User, email=email)
    if default_token_generator.check_token(user, code):
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token)
        })
    return Response(request.data, status.HTTP_400_BAD_REQUEST)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAuthenticated, IsRoleAdminOrSuperuser)

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated], url_path='me')
    def user_profile(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateListDestroyViewSet(CreateModelMixin,
                               ListModelMixin,
                               DestroyModelMixin,
                               GenericViewSet):
    pass


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsRoleAdminOrSuperuserOrReadOnly, ]
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['name', ]
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    lookup_field = 'slug'
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['name', ]
    lookup_field = 'slug'


class TitlesViewSet(ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('id')
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrReadOnly, ]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TitleCreateSerializer
        return TitleListSerializer


class ReviewViewSet(ModelViewSet):
    '''A class to work with Reviews through API'''
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrStaffOrReadOnly,
    ]

    def get_queryset(self):
        '''
        This view should return a list of all the Reviews
        for the current Title.
        '''
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        '''
        Review is added to the specified in URL title by review's author
        '''
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        queryset = Review.objects.filter(
            author=self.request.user,
            title=title
        )
        if queryset.exists():
            raise serializers.ValidationError('Already reviewed')
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ModelViewSet):
    '''A class to work with Comments through API'''
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrStaffOrReadOnly,
    ]

    def get_queryset(self):
        '''
        This view should return a list of all the comments
        for the current Review.
        '''
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return Comment.objects.filter(review=review)

    def perform_create(self, serializer):
        '''
        Comment is added to the specified in URL review by comment's author
        '''
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
