from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AcordoParcelaViewSet

router = DefaultRouter()
router.register(r'', AcordoParcelaViewSet, basename='acordo-parcela')
urlpatterns = [path('', include(router.urls))]
