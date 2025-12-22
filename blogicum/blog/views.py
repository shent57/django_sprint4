from django.views.generic import (
    CreateView, UpdateView, DeleteView, DetailView,
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime
from django.urls import reverse_lazy, reverse
from blog.models import Post, Category
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.utils import timezone
from blog.forms import PostForm

# Create your views here.

User = get_user_model()

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    
    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})
    

class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            return redirect('blog:detail', pk=self.object.pk)
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            return redirect('blog:detail', pk=self.object.pk)
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('blog:detail', kwargs={'pk': self.object.pk})
    
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user and not request.user.is_staff:
            return redirect('blog:detail', pk=self.object.pk)
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user and not request.user.is_staff:
            return redirect('blog:detail', pk=self.object.pk)
        return super().post(request, *args, **kwargs)
    
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.is_published:
            if self.object.author != request.user:
                raise Http404("Пост не найден")
        
        if not self.object.category.is_published:
            if self.object.author != request.user:
                raise Http404("Пост не найден")
        
        if self.object.pub_date > timezone.now():
            if self.object.author != request.user:
                raise Http404("Пост не найден")
        
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.filter(
            is_published=True
        ).select_related('author').order_by('created_at')
        return context
    
@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:detail', pk=pk)


def profile_view(request, username):
    template = 'blog/profile.html'
    profile = get_object_or_404(User, username=username)
    
    if request.user == profile:
        user_posts = Post.objects.filter(
            author=profile).order_by('-pub_date')
    else:
        user_posts = Post.objects.filter(
            author=profile,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')
        
    for post in user_posts:
        post.comment_count = post.comments.filter(is_published=True).count()
    
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    for post in page_obj:
        post.comment_count = post.comments.filter(is_published=True).count()
        
    context = {
        'profile' : profile,
        'page_obj' : page_obj,
    }
    return render(request, template, context)


def index(request):
    template = 'blog/index.html'
    post_list = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).select_related(
        'category', 'author', 'location'
    ).order_by(
        '-pub_date'
    )
    
    for post in post_list:
        post.comment_count = post.comments.filter(is_published=True).count()
        
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    
    for post in page_obj.object_list:
        post.comment_count = post.comments.filter(is_published=True).count()
        
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).select_related(
        'author', 'location'
    ).order_by(
        '-pub_date'
    )
    
    for post in post_list:
        post.comment_count = post.comments.filter(is_published=True).count()
        
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    for post in page_obj.object_list:
        post.comment_count = post.comments.filter(is_published=True).count()
        
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, template, context)

@login_required
def edit_profile(request):
    template = 'blog/user.html'
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, template, {'form': form})

@login_required
def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)
    
    if comment.author != request.user:
        return redirect('blog:detail', pk=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:detail', pk=post_id)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'blog/comment.html', {
        'form': form,
        'post': post,
        'comment': comment,
    })
    
@login_required
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)
    
    if comment.author != request.user:
        return redirect('blog:detail', pk=post_id)
    
    if request.method != 'POST':
        return render(request, 'blog/comment.html', {
            'post': post,
            'comment': comment,
        })
    
    comment.delete()
    return redirect('blog:detail', pk=post_id)