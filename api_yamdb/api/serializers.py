import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Category, Comment, Genre, Review, Title

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role',)
        model = User


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre
        lookup_field = 'slug'


class TitleListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'category',
            'genre',
            'description'
        )
        model = Title


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )

    def validate(self, data):
        if data.get('year') is not None:
            current_date_time = datetime.datetime.now()
            date = current_date_time.date()
            if (data.get('year') <= 0 or data.get('year') > date.year):
                raise serializers.ValidationError('Incorrect year')
            return data
        return data

    class Meta:
        fields = '__all__'
        model = Title


class CommentSerializer(serializers.ModelSerializer):
    '''Serializer class for comments'''
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username',
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('review', )
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer class for reviews"""
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username',
    )

    def validate(self, data):
        """
        Check that score between 1..10
        """
        if (data.get('score') > 10 or data.get('score') < 1):
            raise serializers.ValidationError('Score must be between 1..10')
        return data

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review
