from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('check_auth/', views.check_auth_view, name='check_auth'),
    path('logout/', views.logout_view, name='logout'),
    path('upload_course/', views.upload_course_view, name='upload_course'),
    path('set_thinking_type/', views.set_thinking_type_view, name='set_thinking_type'),
    path('generate_tasks/', views.generate_tasks_view, name='generate_tasks'),
    path('get_task_details/', views.get_task_details_view, name='get_task_details'),
    path('get_dashboard_data/', views.get_dashboard_data_view, name='get_dashboard_data'),
    path('complete_task/', views.complete_task_view, name='complete_task'),
    path('get_results/', views.get_results_view, name='get_results'),
]
