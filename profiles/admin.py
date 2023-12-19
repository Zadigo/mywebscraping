from django.contrib import admin
from django.db.models.functions import Lower
from django.contrib.messages import add_message, SUCCESS
from profiles.constants import OF_INTEREST
from profiles.models import Company, LinkedinProfile


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'linkedin']
    search_fields = ['name']
    date_hierarchy = 'created_on'


@admin.register(LinkedinProfile)
class LinkedinProfilesAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'lastname', 'position', 'url', 'of_interest']
    search_fields = ['company__name', 'position']
    date_hierarchy = 'created_on'
    list_filter = ['of_interest']
    actions = ['mark_of_interest']

    def mark_of_interest(self, request, queryset):
        lowered_positions = queryset.annotate(lowered_position=Lower('position'))
        total_count = 0
        for item in OF_INTEREST:
            for instance in lowered_positions:
                if item in instance.lowered_position:
                    instance.of_interest = True
                    instance.save()
                    total_count = total_count + 1
        add_message(request, SUCCESS, f'{total_count} transformed')
