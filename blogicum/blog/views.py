from datetime import datetime as dt

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView,)

from blog.forms import CommentForm, PostForm
from blog.models import Category, Comment, Post, User

PAGINATE_BY_CONSTANT = 10


class CommentMixin:
    model = Comment
    fields = ('text',)
    template_name = 'blog/comment.html'
    success_url = '/posts/{post_id}/'
    pk_url_kwarg = 'comment_id'
    login_url = '/auth/login/'

    def dispatch(self, request, *args, **kwargs):
        # Проерка яляется ли текущий пользователь автором Поста
        obj = self.get_object()
        if obj.author != self.request.user:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)


class PostMixin:
    model = Post
    template_name = 'blog/create.html'


class PostFormMixin:
    form_class = PostForm


class PostUserRedirectMixin:
    def dispatch(self, request, *args, **kwargs):
        # Проверка является ли текущий пользователь автором Поста + редирект
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect(self.get_login_url())
        return super().dispatch(request, *args, **kwargs)


class PostCreateView(LoginRequiredMixin, PostFormMixin, PostMixin, CreateView):
    login_url = '/auth/login/'

    def get_success_url(self):
        # Определяем страницу для success_url
        username = self.request.user.username
        return f'/profile/{username}/'

    def form_valid(self, form):
        # Автозаполняем поле Автор, данные берем из запроса
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin,
                     PostMixin,
                     PostFormMixin,
                     PostUserRedirectMixin,
                     UpdateView):
    success_url = '/posts/{id}/'

    def get_login_url(self):
        return self.success_url.format(id=self.kwargs['pk'])


class PostDeleteView(LoginRequiredMixin,
                     PostMixin,
                     PostUserRedirectMixin,
                     DeleteView):
    def get_success_url(self):
        return reverse('blog:index')

    def get_login_url(self):
        # Определяем куда направить незалогиненного пользователя
        return f'/posts/{self.kwargs["pk"]}/'


class PostListView(ListView):
    template_name = 'blog/index.html'
    model = Post
    paginate_by = PAGINATE_BY_CONSTANT

    def get_queryset(self):
        queryset = Post.objects.select_related(
            'category',
            'location',
            'author',
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=dt.now(tz=timezone.get_current_timezone()),
        ).order_by('-pub_date').annotate(comment_count=Count('comment'))
        return queryset


class PostDetailView(PostMixin, PostFormMixin, DetailView):
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        # context = super().get_context_data(**kwargs)
        # context['form'] = CommentForm()
        # context['comments'] = (
        #     self.object.comment.select_related('author')
        # )
        return dict(
            **super().get_context_data(**kwargs),
            form=CommentForm(),
            comments=self.object.comment.select_related('author'),
        )


class CategoryPosts(PostMixin, ListView):
    template_name = 'blog/category.html'
    model = Post
    paginate_by = PAGINATE_BY_CONSTANT

    def get_queryset(self):
        return Post.objects.select_related(
            'author', 'location', 'category'
        ).annotate(comment_count=Count('comment')).filter(
            category__slug=self.kwargs['category'],
            is_published=True,
            category__is_published=True,
            pub_date__lte=dt.now(tz=timezone.get_current_timezone()),
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            category=get_object_or_404(
                Category.objects.filter(
                    slug=self.kwargs['category'],
                    is_published=True
                )
            )
        )


class Profile(ListView):
    template_name = 'blog/profile.html'
    model = Post
    paginate_by = PAGINATE_BY_CONSTANT
    form_class = PostForm

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('author'))
        base_query = Post.objects.select_related(
                'author',
                'category',
                'location',
            ).annotate(
                comment_count=Count('comment')
            ).filter(author=user).order_by('-pub_date')
        if user == self.request.user:
            queryset = base_query
        else:
            queryset = base_query.filter(
                is_published=True,
                pub_date__lte=dt.now(tz=timezone.get_current_timezone()),
            )
        return queryset

    def get_context_data(self, **kwargs):
        return dict(
            **super(Profile, self).get_context_data(**kwargs),
            profile=get_object_or_404(
                User, username=self.kwargs.get('author')
            )
        )


class EditProfile(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    model = User
    fields = ('first_name', 'last_name', 'username', 'email')
    success_url = '/profile/{username}/'
    login_url = '/auth/login/'

    def get_object(self, queryset=None):
        return User.objects.filter(username=self.request.user).first()


class CommentCreateView(LoginRequiredMixin, CreateView):
    template_name = 'blog/comment.html'
    object = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.object
        form.instance.post_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', args={self.kwargs['pk']})


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    pass


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    pass
