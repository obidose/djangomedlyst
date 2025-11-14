from django.urls import path
from . import views

urlpatterns = [
    path('', views.patient_list, name='patient_list'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patient/<int:patient_id>/referral/', views.referral_workflow, name='referral_workflow'),
    path('patient/<int:patient_id>/clerking/', views.clerking_workflow, name='clerking_workflow'),
    path('patient/<int:patient_id>/ptwr/', views.ptwr_workflow, name='ptwr_workflow'),
    path('patient/<int:patient_id>/ward-round/', views.general_ward_round, name='general_ward_round'),
    path('patient/<int:patient_id>/consult/', views.consult_request, name='consult_request'),
    path('patient/<int:patient_id>/task/', views.add_task, name='add_task'),
]
