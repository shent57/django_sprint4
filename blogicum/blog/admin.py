from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Category

from .models import Location

from .models import Post, MyUser

admin.site.empty_value_display = 'Не задано'


UserAdmin.fieldsets += (
    ('Extra Fields', {'fields' : ('bio',)}),
)

class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'category',
        'location',
        'author',
        'pub_date'
    )

    list_editable = (
        'is_published',
        'category',
        'location'
    )

    search_fields = ('title', 'text')
    list_filter = ('category', 'is_published', 'pub_date')
    list_display_links = ('title',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published'
    )

    list_editable = ('is_published',)
    search_fields = ('title',)


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published'
    )

    list_editable = ('is_published',)
    search_fields = ('name',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(MyUser, UserAdmin)