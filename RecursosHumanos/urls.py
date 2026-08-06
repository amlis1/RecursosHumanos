from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Vacaciones import views as vac_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', vac_views.CustomLoginView.as_view(), name='login'),
    path('register/', vac_views.register, name='register'),
    path('logout/', vac_views.custom_logout, name='logout'),
    path('clear-welcome/', vac_views.clear_welcome_flag, name='clear_welcome'),
    path('tutorial-pasos/', vac_views.tutorial_pasos, name='tutorial_pasos'),
    path('sw.js', vac_views.service_worker, name='service_worker'),
    path('', include('Vacaciones.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
