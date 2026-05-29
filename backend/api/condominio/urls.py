from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CondominioViewSet, ConfiguracaoMultaViewSet

router = DefaultRouter()
router.register(r'', CondominioViewSet, basename='condominio')
router.register(r'configuracoes-multa',ConfiguracaoMultaViewSet,basename='configuracao-multa')
urlpatterns = [path('', include(router.urls))]
