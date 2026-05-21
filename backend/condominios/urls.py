from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from api.usuarios.views import CustomTokenView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/token/',           CustomTokenView.as_view(),    name='token_obtain_pair'),
    path('api/token/refresh/',   TokenRefreshView.as_view(),   name='token_refresh'),
    path('api/usuarios/',        include('api.usuarios.urls')),
    path('api/acordo/', include('api.acordo.urls')),
    path('api.cobranca', include('api.cobranca.urls')),
    path('api.condominio', include('api.condominio.urls')),
    path('api.historico', include('api.historico.urls')),
    path('api.unidade', include('api.unidade.urls')),
]
