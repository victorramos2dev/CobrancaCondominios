from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UnidadeViewSet

router = DefaultRouter()
router.register(r'', UnidadeViewSet, basename='unidade')
urlpatterns = [path('', include(router.urls))]
