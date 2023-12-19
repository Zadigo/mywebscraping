from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from mylinkedin import views

urlpatterns = [
    path('api/v1/reviews/', include('reviews.api.urls')),
    path('reviews/', include('reviews.urls')),
    path('linkedin/', include('profiles.urls')),
    path('admin/', admin.site.urls),
    re_path(r'^upload$', views.HomeView.as_view(), name='file_upload'),
    re_path(r'^$', views.HomeView.as_view(), name='home')
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
