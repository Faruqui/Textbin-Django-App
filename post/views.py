from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Post

# Create your views here.


def home(request):
    context = {
        "title": "Home",
        "posts": Post.objects.order_by("-date_updated")[:10],
    }

    return render(request, "post/home.html", context)


def about(request):
    return render(request, "post/about.html", {"title": "About"})


class UserPostListView(ListView):
    model = Post
    template_name = "post/user_posts.html"
    context_object_name = "posts"
    ordering = ["-date_updated"]

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        return Post.objects.filter(author=user).order_by("-date_updated")


class PostDetailView(DetailView):
    model = Post


class PostCreateView(CreateView):
    model = Post
    fields = ["title", "content"]

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
            return super().form_valid(form)
        else:
            form.instance.author = None
            return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ["title", "content"]
    template_name = "post/post_update.html"

    def form_valid(self, form):
        form.instance.date_updated = timezone.now()
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_staff:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = "/"

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_staff:
            return True
        return False

    def delete(self, *args, **kwargs):
        messages.success(self.request, "Post Deleted from database")
        return super().delete(*args, **kwargs)