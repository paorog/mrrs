from django.contrib import admin
from mrrs.app.models import System, Department, Designation, Role, UserProfile, Kpi, Industry, Duration, Service, \
    Content, Nps
# Register your models here.
#


class RoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'active_flag')
    list_filter = ('role', 'active_flag')
    search_fields = ('role',)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department', 'active_flag')
    list_filter = ('department', 'active_flag')
    search_fields = ('department',)


class DesignationAdmin(admin.ModelAdmin):
    list_display = ('department','designation', 'active_flag')
    list_filter = ('department__department',)
    search_fields = ('department___department',)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('profile_id', 'fullname', 'role', 'department', 'designation')
    list_filter = ('user__last_name', 'user__first_name')
    search_fields = ('user__last_name', 'user__first_name', 'role', 'department', 'designation')

    def fullname(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name


class KpiAdmin(admin.ModelAdmin):
    list_display = ('id', 'kpi')
    list_filter = ('id', 'kpi')
    search_fields = ('id', 'kpi')


class IndustryAdmin(admin.ModelAdmin):
    list_display = ('id', 'industry')
    list_filter = ('id', 'industry')
    search_fields = ('id', 'industry')


class DurationAdmin(admin.ModelAdmin):
    list_display = ('duration', 'duration_months', 'duration_years')
    list_filter = ('duration', 'duration_months', 'duration_years')
    search_fields = ('duration', 'duration_months', 'duration_years')


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'service')
    list_filter = ('id', 'service')
    search_fields = ('id', 'service')


class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'content')
    list_filter = ('id', 'content')
    search_fields = ('id', 'content')


class NpsAdmin(admin.ModelAdmin):
    list_display = ('id', 'nps')
    list_filter = ('id', 'nps')
    search_fields = ('id', 'nps')


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(System)
admin.site.register(Role, RoleAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Designation, DesignationAdmin)
admin.site.register(Kpi, KpiAdmin)
admin.site.register(Industry, IndustryAdmin)
admin.site.register(Duration, DurationAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Content, ContentAdmin)
admin.site.register(Nps, NpsAdmin)

