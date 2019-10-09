from django.contrib.auth.models import User
from mrrs.app.models import UserProfile, Role, Department, Designation, Kpi, Industry, Duration, Service, Content,ServiceCreated, ContentCreated, Invoice, Client, Kpi, KpiCreated, Nps, NpsCreated
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
#import rest_framework_filters as filters
from django_countries.fields import CountryField
from django_countries import countries
from django.http import HttpResponse, JsonResponse
from django.core import serializers as serializer
from drf_writable_nested import WritableNestedModelSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'is_active')
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

        
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = UserProfile
        fields = ('user', 'department', 'designation', 'role')

    def create(self, validated_data):
        #return validated_data
        # randpass = User.objects.make_random_password(length=14)
        # instance.user.set_password(randpass)
        # instance.user.save()
        user_data = validated_data.pop('user')
        randpass = User.objects.make_random_password(length=14)
        save_user = User.objects.create(**user_data, password=make_password(randpass))
        save_user.save()
        user_profile = UserProfile.objects.create(user=save_user, **validated_data)
        # current_site = get_current_site(request)
        mail_subject = 'Your Login to Mrrs'
        mail_plain = 'MRRS App'
        mail_sender = 'admin.mrrs@heroesofdigital.com'
        mail_receiver = user_data.get('email')
        mail_body = render_to_string('email/addhero.html', {'username': user_data.get('username'), 'email': user_data.get('email'), 'password': randpass})

        send_mail(
            mail_subject,
            mail_plain,
            mail_sender,
            [mail_receiver],
            html_message=mail_body,
        )
        return user_profile

    def update(self, instance, validated_data): 
        user_data = validated_data.pop('user')
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.user.save()
        instance.save()
        return instance


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ('id', 'role')


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ('id', 'department')


class DesignationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Designation
        fields = ('department', 'id', 'designation')


class HeroManagerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    role = RoleSerializer()
    department = DepartmentSerializer()
    designation = DesignationSerializer()

    class Meta:
        model = UserProfile
        fields = ('user', 'department', 'designation', 'role')

    # def create(self, validated_data):
    #     #return validated_data
    #     # randpass = User.objects.make_random_password(length=14)
    #     # instance.user.set_password(randpass)
    #     # instance.user.save()
    #     user_data = validated_data.pop('user')
    #     randpass = User.objects.make_random_password(length=14)
    #     save_user = User.objects.create(**user_data, password=make_password(randpass))
    #     save_user.save()
    #     user_profile = UserProfile.objects.create(user=save_user, **validated_data)
    #     return user_profile

    # def update(self, instance, validated_data): 
    #     user_data = validated_data.pop('user')
    #     for attr, value in user_data.items():
    #         setattr(instance.user, attr, value)

    #     # user_role = validated_data.pop('role')
    #     # user_role = UserProfile.objects.filter(user_id=1).update(role=2)
    #     # user_role.save()
    #     # retrieve Profile
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)

    #     instance.user.save()
    #     instance.save()
    #     return instance

# class DesignationFilter(filters.FilterSet):
#     designation = filters.CharFilter(name="department__dept_code")

#     class Meta:
#         model = Product
#         fields = ['category', 'in_stock', 'designation']
#         
#


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class DurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Duration
        fields = ('id', 'duration', 'duration_months', 'duration_years')


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class ServiceCreatedManagerSerializer(serializers.ModelSerializer):
    #service = ServiceSerializer(many=False)

    class Meta:
        model = ServiceCreated
        fields = ('service', 'service_qty', 'service_fee')


class ServiceCreatedSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(many=False)

    class Meta:
        model = ServiceCreated
        fields = ('service', 'service_qty', 'service_fee', 'service_status')


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'


class ContentCreatedSerializer(serializers.ModelSerializer):
    content = ContentSerializer(many=False)

    class Meta:
        model = ContentCreated
        fields = ('content', 'content_qty', 'content_status')


class ContentCreatedManagerSerializer(serializers.ModelSerializer):
    #content = ContentSerializer(many=False)

    class Meta:
        model = ContentCreated
        fields = ('content', 'content_qty', 'content_status')


class KpiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kpi
        fields = '__all__'


class KpiCreatedSerializer(serializers.ModelSerializer):
    kpi = KpiSerializer(many=False)

    class Meta:
        model = KpiCreated
        fields = ('id', 'kpi', 'kpi_text')


class KpiCreatedManagerSerializer(serializers.ModelSerializer):
    #kpi = KpiSerializer(many=False)

    class Meta:
        model = KpiCreated
        fields = ('id', 'kpi', 'kpi_text')


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ("xero_id", "created", "client_name", 'management_fee', "other_revenue", "media_fees", "contract", "industry", "company_size",
                "pm", "writer", "start_date", "end_date", "duration")


class ClientListManagerSerializer(serializers.ModelSerializer):
    services = ServiceCreatedSerializer(many=True)
    contents = ContentCreatedSerializer(many=True)
    kpi = KpiCreatedSerializer(many=True)

    class Meta:
        model = Client
        fields = ('id', 'xero_id', 'created', 'client_name', "other_revenue", "media_fees", "contract", "industry", "company_size",
                "pm", "writer", 'services', 'management_fee', 'contents', 'kpi', 'duration', 'start_date', 'end_date', 'created_at')


class ClientManagerSerializer(WritableNestedModelSerializer):
    #client = ClientSerializer(many=False, required=False)
    services = ServiceCreatedManagerSerializer(many=True, required=False)
    contents = ContentCreatedManagerSerializer(many=True, required=False)
    kpi = KpiCreatedManagerSerializer(many=True, required=False)

    class Meta:
        model = Client
        fields = ('id', 'xero_id', 'created', 'client_name', "other_revenue", "media_fees", "contract", "industry", "company_size",
                "pm", "writer", 'services', 'management_fee', 'contents', 'kpi', 'duration', 'start_date', 'end_date', 'created_at')

    # def create(self, validated_data):
    #     client_data = validated_data.pop('client')
    #     services_data = validated_data.pop('services')
    #     contents_data = validated_data.pop('contents')
    #     kpis_data = validated_data.pop('kpi')
    #
    #     save_client = Client.objects.create(**client_data)
    #
    #     for service_data in services_data:
    #         save_service = ServiceCreated.objects.create(**service_data)
    #         save_client.services.add(save_service)
    #
    #     for content_data in contents_data:
    #         save_content = ContentCreated.objects.create(**content_data)
    #         save_client.contents.add(save_content)
    #
    #     for kpi_data in kpis_data:
    #         save_kpi = KpiCreated.objects.create(**kpi_data)
    #         save_client.kpi.add(save_kpi)
    #
    #     return save_client


class ContentCreatedSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    services = ServiceSerializer()

    class Meta:
        model = UserProfile
        fields = ('user', 'department', 'designation', 'role')


class IndustrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Industry
        fields = '__all__'


class NpsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Nps
        fields = '__all__'


class NpsCreatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = NpsCreated
        fields = '__all__'
