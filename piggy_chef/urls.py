from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login_page'),
    path('upload/', TemplateView.as_view(template_name='upload.html'), name='upload_page'),
    path('select/', TemplateView.as_view(template_name='select.html'), name='select_page'),
    path('start/', TemplateView.as_view(template_name='start.html'), name='start_page'),
    path('key_info/', TemplateView.as_view(template_name='key_info.html'), name='key_info_page'),
    path('results/', TemplateView.as_view(template_name='results.html'), name='results_page'),
    path('task_detail/', TemplateView.as_view(template_name='task_detail.html'), name='task_detail_page'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile_page'),
    path('offline/', TemplateView.as_view(template_name='offline.html'), name='offline_page'),
]
