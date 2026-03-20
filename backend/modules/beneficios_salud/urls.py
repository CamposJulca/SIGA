from django.urls import path
from .views import (
    UploadView, ArchivoListView, ArchivoDetailView,
    BeneficioListView, ExportarExcelView, NovedadesView, DashboardView,
    # Medicina Prepagada
    CruceView,
    PoliticaView, PoliticaDetailView,
    PensionadosView, PensionadoDetailView,
    AuxilioExternoView, AuxilioExternoDetailView,
    PlanillaListView, PlanillaCalcularView, PlanillaDetailView, PlanillaExportarView,
    CausacionView, ConciliacionView, InformeEFRView,
)

urlpatterns = [
    # Existing endpoints
    path('upload/', UploadView.as_view()),
    path('archivos/', ArchivoListView.as_view()),
    path('archivos/<int:pk>/', ArchivoDetailView.as_view()),
    path('beneficios/', BeneficioListView.as_view()),
    path('exportar/', ExportarExcelView.as_view()),
    path('novedades/', NovedadesView.as_view()),
    path('dashboard/', DashboardView.as_view()),
    # Medicina Prepagada
    path('cruce/', CruceView.as_view()),
    path('politica/', PoliticaView.as_view()),
    path('politica/<int:pk>/', PoliticaDetailView.as_view()),
    path('pensionados/', PensionadosView.as_view()),
    path('pensionados/<int:pk>/', PensionadoDetailView.as_view()),
    path('auxilio-externo/', AuxilioExternoView.as_view()),
    path('auxilio-externo/<int:pk>/', AuxilioExternoDetailView.as_view()),
    path('planilla/', PlanillaListView.as_view()),
    path('planilla/calcular/', PlanillaCalcularView.as_view()),
    path('planilla/<int:pk>/', PlanillaDetailView.as_view()),
    path('planilla/<int:pk>/exportar/', PlanillaExportarView.as_view()),
    path('causacion/', CausacionView.as_view()),
    path('conciliacion/', ConciliacionView.as_view()),
    path('informe-efr/', InformeEFRView.as_view()),
]
