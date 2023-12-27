from django.urls import re_path
from reviews.api import views

app_name = 'api_reviews'

urlpatterns = [
    re_path(r'^business/create$', views.create_business),
    re_path(r'^bulk$', views.create_bulk_reviews),
    re_path(r'^create$', views.create_review)
]
