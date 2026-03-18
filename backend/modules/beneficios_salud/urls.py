from django.urls import path
from .views import (
    UploadView, ArchivoListView, ArchivoDetailView,
    BeneficioListView, ExportarExcelView, NovedadesView, DashboardView,
)

urlpatterns = [
    path('upload/', UploadView.as_view()),
    path('archivos/', ArchivoListView.as_view()),
    path('archivos/<int:pk>/', ArchivoDetailView.as_view()),
    path('beneficios/', BeneficioListView.as_view()),
    path('exportar/', ExportarExcelView.as_view()),
    path('novedades/', NovedadesView.as_view()),
    path('dashboard/', DashboardView.as_view()),
]
