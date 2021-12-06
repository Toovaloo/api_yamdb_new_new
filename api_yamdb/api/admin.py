from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    '''Admin Panel for Users'''
    list_display = (
        'pk', 'username', 'email',
        'first_name', 'last_name', 'role', 'bio'
    )
    empty_value_display = '-пусто-'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    '''Admin Panel for Categories'''
    list_display = ('pk', 'name', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    '''Admin Panel for Genres'''
    list_display = ('pk', 'name', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    '''Admin Panel for Titles'''
    list_display = ('pk', 'name', 'year', 'description', 'category')
    empty_value_display = '-пусто-'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    '''Admin Panel for Reviews'''
    list_display = ('pk', 'text', 'pub_date', 'author', 'score', 'title')
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    '''Admin Panel for Comments'''
    list_display = ('pk', 'text', 'pub_date', 'author', 'review')
    list_filter = ('pub_date',)
    search_fields = ('text', 'slug', 'description')
    empty_value_display = '-пусто-'
