from django.urls import re_path

from reviews import views


app_name = 'reviews'

urlpatterns = [
    re_path(r'download', views.DownloadFileView.as_view(), name='download_csv_file'),
    re_path(r'^create$', views.CreateReviewsView.as_view(), name='file_upload'),
    re_path(r'^(?P<pk>\d+)/sentiment$', views.caculate_review_sentiment, name='calculate_sentiment'),
    re_path(r'^(?P<pk>\d+)$', views.CompanyView.as_view(), name='list_reviews'),
    re_path(r'^$', views.ListBusinesses.as_view(), name='list_companies')
]
