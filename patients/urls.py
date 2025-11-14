from django.urls import path
from . import views

urlpatterns = [
    path('', views.patient_list, name='patient_list'),
    path('take-list/', views.take_list, name='take_list'),
    path('weekend-review/', views.weekend_review_list, name='weekend_review_list'),
    path('consults/', views.consults_list, name='consults_list'),
    path('consult/<int:consult_id>/update/', views.update_consult_status, name='update_consult_status'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patient/<int:patient_id>/edit/', views.edit_patient_info, name='edit_patient_info'),
    path('patient/<int:patient_id>/referral/', views.referral_workflow, name='referral_workflow'),
    path('patient/<int:patient_id>/change-specialty/', views.change_specialty, name='change_specialty'),
    path('patient/<int:patient_id>/clerking/', views.clerking_workflow, name='clerking_workflow'),
    path('patient/<int:patient_id>/ptwr/', views.ptwr_workflow, name='ptwr_workflow'),
    path('patient/<int:patient_id>/ward-round/', views.general_ward_round, name='general_ward_round'),
    path('patient/<int:patient_id>/consult/', views.consult_request, name='consult_request'),
    path('patient/<int:patient_id>/task/', views.add_task, name='add_task'),
    path('patient/<int:patient_id>/complete-admission/', views.complete_admission, name='complete_admission'),
    path('patient/<int:patient_id>/toggle-priority/', views.toggle_priority, name='toggle_priority'),
    path('patient/<int:patient_id>/toggle-weekend-review/', views.toggle_weekend_review, name='toggle_weekend_review'),
    path('patient/<int:patient_id>/update-team/', views.update_team, name='update_team'),
    path('task/<int:task_id>/edit/', views.edit_task, name='edit_task'),
]
