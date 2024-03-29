from django.contrib import admin

from blog.models import Category, Comment, Location, Post


class PostsInline(admin.StackedInline):
    model = Post
    extra = 0


@admin.register(Category, Location)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (PostsInline,)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
    )
    list_editable = (
        'is_published',
        'category',
    )
    list_filter = (
        'category',
        'author',
    )
    search_fields = ('title',)
    list_display_links = ('title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
        'created_at',
    )
