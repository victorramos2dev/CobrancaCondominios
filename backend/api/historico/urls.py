from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HistoricoStatusViewSet

router = DefaultRouter()
router.register(r'', HistoricoStatusViewSet, basename='historico')
urlpatterns = [path('', include(router.urls))]
