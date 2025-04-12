from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('family.urls')),
    path('api/news/', include('news.urls')),
    path('api/account/', include('account.urls')),
    path('api/filemanager/', include('filemanager.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
