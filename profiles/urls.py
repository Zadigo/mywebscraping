from django.urls import re_path
from profiles import views

app_name = 'linkedin'

urlpatterns = [
    re_path(r'^upload$', views.UploadFileView.as_view(), name='file_upload'),
    re_path(r'^companies/(?P<pk>\d+)$', views.CompanyView.as_view(), name='company_profiles'),
    re_path(r'^$', views.CompaniesView.as_view(), name='list_companies')
]


