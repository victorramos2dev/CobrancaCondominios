from django.urls import path
from .views import DashboardView, InadimplenciaResumoView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
]
