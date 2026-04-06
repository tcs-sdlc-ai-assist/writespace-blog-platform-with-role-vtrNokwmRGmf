from django.urls import path

from blog.views import (
    admin_dashboard,
    blog_create,
    blog_delete,
    blog_detail,
    blog_edit,
    blog_list,
    landing_page,
    user_management,
)

urlpatterns = [
    path('', landing_page, name='landing'),
    path('blogs/', blog_list, name='blog_list'),
    path('blog/<uuid:id>/', blog_detail, name='blog_detail'),
    path('write/', blog_create, name='blog_create'),
    path('edit/<uuid:id>/', blog_edit, name='blog_edit'),
    path('delete/<uuid:id>/', blog_delete, name='blog_delete'),
    path('admin-panel/', admin_dashboard, name='admin_dashboard'),
    path('users/', user_management, name='user_management'),
]