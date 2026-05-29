from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AcordoViewSet, AcordoParcelaViewSet

router = DefaultRouter()
router.register(r'', AcordoViewSet, basename='acordo')
urlpatterns = [path('', include(router.urls))]

router_parcelas = DefaultRouter()
router_parcelas.register(r'', AcordoParcelaViewSet, basename='acordo-parcela')
