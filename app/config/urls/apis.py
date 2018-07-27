from django.urls import path, include

urlpatterns = [
    path('posts/', include('posts.urls.apis')),
    path('users/', include('members.urls.apis')),
]
