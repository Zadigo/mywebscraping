from django.contrib import admin

from reviews.models import Company, Review


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_on']
    date_hierarchy = 'created_on'
    actions = ['download_csv']
    readonly_fields = ['company_id']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['review_id', 'rating', 'created_on']
    date_hierarchy = 'created_on'
    readonly_fields = ['review_id']
    list_per_page = 50
