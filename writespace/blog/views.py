from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import AdminCreateUserForm
from blog.forms import PostForm
from blog.models import Post


def staff_required(user):
    return user.is_staff


def landing_page(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin-panel/')
        return redirect('/blogs/')

    latest_posts = Post.objects.select_related('author').order_by('-created_at')[:3]
    return render(request, 'blog/landing.html', {'posts': latest_posts})


@login_required
def blog_list(request):
    posts = Post.objects.select_related('author').order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'posts': posts})


@login_required
def blog_detail(request, id):
    post = get_object_or_404(Post.objects.select_related('author'), id=id)
    is_owner = post.author == request.user
    can_edit = is_owner or request.user.is_staff
    return render(request, 'blog/blog_detail.html', {
        'post': post,
        'is_owner': is_owner,
        'can_edit': can_edit,
    })


@login_required
def blog_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('/blog/' + str(post.id) + '/')
    else:
        form = PostForm()

    return render(request, 'blog/blog_form.html', {'form': form, 'editing': False})


@login_required
def blog_edit(request, id):
    post = get_object_or_404(Post, id=id)

    if not (post.author == request.user or request.user.is_staff):
        return HttpResponseForbidden(render(request, 'errors/403.html').content)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('/blog/' + str(post.id) + '/')
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/blog_form.html', {'form': form, 'editing': True, 'post': post})


@login_required
def blog_delete(request, id):
    post = get_object_or_404(Post, id=id)

    if not (post.author == request.user or request.user.is_staff):
        return HttpResponseForbidden(render(request, 'errors/403.html').content)

    if request.method == 'POST':
        post.delete()
        return redirect('/blogs/')

    return render(request, 'blog/blog_confirm_delete.html', {'post': post})


@login_required
@user_passes_test(staff_required, login_url='/login/')
def admin_dashboard(request):
    total_posts = Post.objects.count()
    total_users = User.objects.count()
    recent_posts = Post.objects.select_related('author').order_by('-created_at')[:5]

    return render(request, 'blog/admin_dashboard.html', {
        'total_posts': total_posts,
        'total_users': total_users,
        'recent_posts': recent_posts,
    })


@login_required
@user_passes_test(staff_required, login_url='/login/')
def user_management(request):
    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'delete':
            user_id = request.POST.get('user_id')
            if user_id:
                user_to_delete = get_object_or_404(User, id=user_id)
                if user_to_delete != request.user:
                    user_to_delete.delete()
            return redirect('/users/')

        else:
            form = AdminCreateUserForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                display_name = form.cleaned_data['display_name']
                role = form.cleaned_data['role']

                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=display_name,
                )
                if role == 'admin':
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()

                return redirect('/users/')
    else:
        form = AdminCreateUserForm()

    users = User.objects.all().order_by('-date_joined')
    return render(request, 'blog/user_management.html', {'form': form, 'users': users})