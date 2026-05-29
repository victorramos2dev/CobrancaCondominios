from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CobrancaViewSet

router = DefaultRouter()
router.register(r'', CobrancaViewSet, basename='cobranca')
urlpatterns = [path('', include(router.urls))]
