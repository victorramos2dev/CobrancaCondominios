from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from api.usuarios.views import CustomTokenView
from api.dashboard.views import InadimplenciaResumoView

urlpatterns = [
    path('admin/', admin.site.urls),
    # JWT
    path('api/token/', CustomTokenView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # CRUD Apps
    path('api/usuarios/', include('api.usuarios.urls')),
    path('api/condominios/', include('api.condominio.urls')),
    path('api/unidades/', include('api.unidade.urls')),
    path('api/cobrancas/', include('api.cobranca.urls')),
    path('api/acordos/', include('api.acordo.urls')),
    path('api/parcelas-acordo/', include('api.acordo.urls_parcelas')),
    path('api/historico/', include('api.historico.urls')),
    # Endpoints inteligentes
    path('api/dashboard/', include('api.dashboard.urls')),
    path('api/inadimplencia/resumo/', InadimplenciaResumoView.as_view(), name='inadimplencia-resumo'),
]
