from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from uuid import uuid4
from django.apps import apps
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField

def increment_user_id():
    set_unique_id = uuid4()
    user_id = str(set_unique_id)[:20]
    return user_id


def new_user_pass():
    randpass = User.objects.make_random_password(length=14)
    return randpass

# def generate_model_code(this_model, code, model_code):
#     model = apps.get_model(app_label='app', model_name=this_model)
#     last_code = model.objects.all().order_by(model_code).last()
#     if not last_code:
#         return code + '001'
#
#     code_id = last_code.dept_code
#     code_int = int(code_id[3:5])
#     new_code_int = code_int + 1
#     new_code_id = code + str(new_code_int).zfill(3)
#     return new_code_id


# def generate_role_code():
#     last_role = Role.objects.all().order_by('role_code').last()
#     if not last_role:
#         return 'RL' + '001'

#     role_id = last_role.role_code
#     role_int = int(role_id[3:5])
#     new_role_int = role_int + 1
#     new_role_id = 'RL' + str(new_role_int).zfill(3)
#     return new_role_id


# def generate_dept_code():
#     last_dept = Department.objects.all().order_by('dept_code').last()
#     if not last_dept:
#         return 'DP' + '001'

#     dept_id = last_dept.dept_code
#     dept_int = int(dept_id[3:5])
#     new_dept_int = dept_int + 1
#     new_dept_id = 'DP' + str(new_dept_int).zfill(3)
#     return new_dept_id


# def generate_desi_code():
#     last_desi = Designation.objects.all().order_by('desi_code').last()
#     if not last_desi:
#         return 'DS' + '001'

#     desi_id = last_desi.desi_code
#     desi_int = int(desi_id[3:5])
#     new_desi_int = desi_int + 1
#     new_desi_id = 'DS' + str(new_desi_int).zfill(3)
#     return new_desi_id


class System(models.Model):
    system_type = models.CharField(max_length=20)
    system_desc = models.CharField(max_length=50)


class Role(models.Model):
    #role_code = models.CharField(max_length=5, default=generate_role_code, editable=False, unique=True)
    role = models.CharField(max_length=50)
    active_flag = models.BooleanField(default=True)

    def __str__(self):
        return self.role


class Department(models.Model):
    #dept_code = models.CharField(max_length=5, default=generate_dept_code, editable=False, unique=True)
    department = models.CharField(max_length=100)
    active_flag = models.BooleanField(default=True)

    def __str__(self):
        return self.department


class Designation(models.Model):
    #desi_code = models.CharField(max_length=5, default=generate_desi_code, editable=False, unique=True)
    #dept_code = models.ForeignKey(Department, to_field="dept_code", db_column="dept_code", on_delete=models.CASCADE)
    department = models.ForeignKey(Department,to_field="id", db_column="department_id", on_delete=models.PROTECT)
    designation = models.CharField(max_length=100)
    active_flag = models.BooleanField(default=True)

    def __str__(self):
        return self.designation


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_id = models.CharField(max_length=20, default=increment_user_id, editable=False)
    role = models.ForeignKey(Role, to_field="id", db_column="role_id", on_delete=models.PROTECT)
    # role = models.OneToOneField(Role, on_delete=models.PROTECT)
    # department = models.OneToOneField(Department, on_delete=models.PROTECT)
    # designation = models.OneToOneField(Designation, on_delete=models.PROTECT)
    department = models.ForeignKey(Department, to_field="id", db_column="department_id", on_delete=models.PROTECT)
    designation = models.ForeignKey(Designation, to_field="id", db_column="designation_id", on_delete=models.PROTECT)

    # def __str__(self):
    #     return self
    # @receiver(post_save, sender=User)
    # def create_user_profile(sender, instance, created, **kwargs):
    #     if created:
    #         Profile.objects.create(user=instance)

    # @receiver(post_save, sender=User)
    # def save_user_profile(sender, instance, **kwargs):
    #     instance.profile.save()


class Kpi(models.Model):
    kpi = models.CharField(max_length=100)


class KpiCreated(models.Model):
    kpi = models.ForeignKey(Kpi, to_field="id", db_column="kpi_id", on_delete=models.CASCADE)
    kpi_text = models.CharField(max_length=100, null=True)

class Industry(models.Model):
    industry = models.CharField(max_length=100)


class Duration(models.Model):
    duration = models.CharField(max_length=10)
    duration_months = models.IntegerField(default=None, blank=True, null=True)
    duration_years = models.IntegerField(default=None, blank=True, null=True)


class Service(models.Model):
    service = models.CharField(max_length=50)


class Content(models.Model):
    content = models.CharField(max_length=100)


class ServiceCreated(models.Model):
    service = models.ForeignKey(Service, to_field="id", db_column="service_id", on_delete=models.CASCADE)
    service_qty = models.IntegerField(null=True, default=1, blank=True)
    service_fee = models.IntegerField()
    service_status = models.ForeignKey(System, to_field="id", db_column="service_status_id", default=None, blank=True,
                                       null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class ContentCreated(models.Model):
    content = models.ForeignKey(Content, to_field="id", db_column="content_id", on_delete=models.CASCADE)
    content_qty = models.IntegerField(null=True, default=None, blank=True)
    content_status = models.ForeignKey(System, to_field="id", db_column="content_status_id", default=None, blank=True,
                                       null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class Client(models.Model):
    xero_id = models.CharField(max_length=50, default=None)
    created = models.ForeignKey(User, to_field="id", db_column="created_id", related_name="created_by", on_delete=models.PROTECT)
    client_name = models.CharField(max_length=100)
    in_churn = models.BooleanField(default=0)
    services = models.ManyToManyField(ServiceCreated)
    management_fee = models.IntegerField(null=True, default=None, blank=True)
    contents = models.ManyToManyField(ContentCreated)
    other_revenue = models.CharField(max_length=100)
    media_fees = models.FloatField(default=0)
    #duration = models.ForeignKey(Duration, to_field="id", db_column="duration_id", on_delete=models.CASCADE)
    duration = models.CharField(max_length=10)
    contract = models.CharField(max_length=100, default=None, blank=True, null=True)
    industry = models.ForeignKey(Industry, to_field="id", db_column="industry_id", on_delete=models.PROTECT)
    company_size = models.CharField(max_length=20)
    pm = models.ForeignKey(User, to_field="id", db_column="pm_id", related_name="client_pm", default=None, blank=True,
                           null=True, on_delete=models.PROTECT)
    writer = models.ForeignKey(User, to_field="id", db_column="writer_id", related_name="client_writer", default=None,
                               blank=True, null=True, on_delete=models.PROTECT)
    kpi = models.ManyToManyField(KpiCreated)
    start_date = models.DateField(default=None, blank=True, null=True)
    end_date = models.DateField(default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class Invoice(models.Model):
    client = models.ForeignKey(Client, to_field="id", db_column="client_id", default=None, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    is_paid = models.BooleanField(default=0)
    week_num = models.IntegerField()


class Nps(models.Model):
    nps = models.CharField(max_length=100)


class NpsCreated(models.Model):
    nps = models.ForeignKey(Nps, to_field="id", db_column="nps_id", default=None, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    service = models.CharField(max_length=100)


class CsmClient(models.Model):
    client = models.ForeignKey(Client, to_field="id", db_column="client_id", default=None, on_delete=models.CASCADE)
    week = models.IntegerField(default=None)
    score = models.IntegerField(default=None)
    nps = models.ManyToManyField(NpsCreated)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

