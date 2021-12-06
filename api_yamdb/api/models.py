from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):

    class Role(models.TextChoices):
        USER = 'user', _('обычный пользователь')
        MODERATOR = 'moderator', _('модератор')
        ADMIN = 'admin', _('администратор')

    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    bio = models.TextField(max_length=500, blank=True)
    role = models.CharField(
        max_length=9,
        choices=Role.choices,
        default='user'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def has_admin_perm(self):
        return (self.role == self.Role.ADMIN or self.is_superuser)

    @property
    def has_moderator_perm(self):
        return (self.role == self.Role.ADMIN
                or self.is_superuser
                or self.role == self.Role.MODERATOR)


USER_MODEL = get_user_model()


class Category(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Категория', unique=True
    )
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Жанр', unique=True
    )
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=200, verbose_name='Произведение')
    year = models.IntegerField(
        null=True, verbose_name='Год выпуска', db_index=True
    )
    description = models.CharField(max_length=200, null=True)
    genre = models.ManyToManyField(Genre, blank=True, related_name='titles')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='titles'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    '''Class for Reviews.
    Reviews are connected to Titles.
    '''
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )
    author = models.ForeignKey(
        USER_MODEL, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.PositiveSmallIntegerField()
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    '''Class for Comments.
    Comments belong to Reviews.
    '''
    author = models.ForeignKey(
        USER_MODEL, on_delete=models.CASCADE, related_name='comments'
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]
