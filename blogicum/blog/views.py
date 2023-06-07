from datetime import datetime as dt


from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import (
    CreateView, ListView, DetailView, UpdateView, DeleteView
)
from django.urls import reverse_lazy, reverse
from django.db.models import Count
from django.http import Http404


from blog.forms import PostForm, CommentForm
from blog.models import Post, Category, User, Comment


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
        # Определяем куда направить незалогиненного пользователя
        id = self.kwargs['pk']
        return f'/posts/{id}/'


class PostDeleteView(LoginRequiredMixin,
                     PostMixin,
                     PostUserRedirectMixin,
                     DeleteView):
    success_url = reverse_lazy('blog:index')

    def get_login_url(self):
        # Определяем куда направить незалогиненного пользователя
        id = self.kwargs['pk']
        return f'/posts/{id}/'


class PostListView(ListView):
    template_name = 'blog/index.html'
    model = Post
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.select_related(
            'category',
            'location',
            'author'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=dt.now(tz=timezone.get_current_timezone())
        ).order_by('-pub_date').annotate(comment_count=Count('comment'))
        return queryset


class PostDetailView(PostMixin, PostFormMixin, DetailView):
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comment.select_related('author')
        )
        return context


class CategoryPosts(PostMixin, ListView):
    template_name = 'blog/category.html'
    model = Post
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.objects.select_related(
            'author', 'location', 'category'
        ).annotate(comment_count=Count('comment')).filter(
            category__slug=self.kwargs['category'],
            is_published=True,
            category__is_published=True,
            pub_date__lte=dt.now(tz=timezone.get_current_timezone())
        ).order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CategoryPosts, self).get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category.objects.filter(slug=self.kwargs['category'],
                                    is_published=True)
        )
        return context


class Profile(ListView):
    template_name = 'blog/profile.html'
    model = Post
    paginate_by = 10
    form_class = PostForm

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('author'))
        if user == self.request.user:
            queryset = Post.objects.select_related(
                'author',
                'category',
                'location'
            ).annotate(
                comment_count=Count('comment')
            ).filter(author=user).order_by('-pub_date')
        else:
            queryset = Post.objects.select_related(
                'author',
                'category',
                'location'
            ).annotate(
                comment_count=Count('comment')
            ).filter(author=user,
                     is_published=True,
                     pub_date__lte=dt.now(tz=timezone.get_current_timezone())
                     ).order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Profile, self).get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User, username=self.kwargs.get('author')
        )
        return context


class EditProfile(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    model = User
    fields = ('first_name', 'last_name', 'username', 'email')
    success_url = '/profile/{username}/'
    login_url = '/auth/login/'

    def get_object(self, queryset=None):
        user = self.request.user
        return User.objects.filter(username=user).first()


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
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    pass


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    pass
