from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import user_passes_test
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


def is_superuser(user):
    # return user.is_superuser
    # return user.is_authenticated
    return True


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('schema/', user_passes_test(is_superuser)(SpectacularAPIView.as_view()), name='schema'),
    path('swagger/', user_passes_test(is_superuser)(SpectacularSwaggerView.as_view()), name='swagger-ui'),
    path('redoc/', user_passes_test(is_superuser)(SpectacularRedocView.as_view()), name='redoc'),
    path('health/', lambda _: JsonResponse({'detail': 'Healthy'}), name='health'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
