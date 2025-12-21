from django.urls import path

from django.contrib.auth.decorators import login_required
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='detail'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('posts/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         login_required(views.edit_comment), name='edit_comment'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('profile/edit/', login_required(views.edit_profile), name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         login_required(views.delete_comment), name='delete_comment'),
    path('posts/<int:pk>/post_detail/', views.PostDetailView.as_view(), name='post_detail'),
]
