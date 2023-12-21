from django.urls import re_path

from reviews import views


app_name = 'reviews'

urlpatterns = [
    re_path(
        r'^download', 
        views.DownloadFileView.as_view(),
        name='download_csv_file'
    ),
    re_path(
        r'^upload$', 
        views.UploadReviewsView.as_view(), 
        name='file_upload'
    ),
    re_path(
        r'^robot$', 
        views.StartRobotView.as_view(), 
        name='start_robot'
    ),
    # re_path(r'^(?P<pk>\d+)/sentiment$', views.caculate_review_sentiment, name='calculate_sentiment'),
    re_path(
        r'^(?P<pk>\d+)$', 
        views.ListReviewsView.as_view(),
        name='list_reviews'
    ),
    re_path(
        r'^$', 
        views.ListCompaniesView.as_view(),
        name='list_companies'
    )
]
