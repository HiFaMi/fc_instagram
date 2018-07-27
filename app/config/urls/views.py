from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .. import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('posts/', include('posts.urls.views')),
    path('members/', include('members.urls.views')),
    path('', views.index, name='index'),
]
urlpatterns += static(
    prefix=settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)
