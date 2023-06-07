from blog import views

from django.urls import path, include
from django.contrib import admin


app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('category/<slug:category>/', views.CategoryPosts.as_view(), name='category_posts'),
    path('admin/', admin.site.urls),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('posts/<int:pk>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('profile/edit/', views.EditProfile.as_view(), name='edit_profile'),
    path('profile/<slug:author>/', views.Profile.as_view(), name='profile'),
]
