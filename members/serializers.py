# members/serializers.py
from rest_framework import serializers
from .models import CustomUser, Donation, DonationRecord, Category, Location, WaterLevel, DonationHistory, Shelter
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import password_validation

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'is_employee',
            'house_number', 'street_name', 'residential_area',
            'postcode', 'city', 'state',
            'phone_number', 'gender',
            'date_joined', 'last_login'
        ]
    def get_full_address(self, obj):
        return obj.full_address()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password',
            'house_number', 'street_name', 'residential_area',
            'postcode', 'city', 'state',
            'phone_number', 'gender'
        ]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )

        user.is_employee = False

        user.house_number = validated_data.get('house_number', '')
        user.street_name = validated_data.get('street_name', '')
        user.residential_area = validated_data.get('residential_area', '')
        user.postcode = validated_data.get('postcode', '')
        user.city = validated_data.get('city', '')
        user.state = validated_data.get('state', '')
        user.phone_number = validated_data.get('phone_number', '')
        user.gender = validated_data.get('gender', '')

        user.save()
        return user

class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email',
            'house_number', 'street_name', 'residential_area',
            'postcode', 'city', 'state',
            'phone_number', 'gender'
        ]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'house_number', 'street_name', 'residential_area', 'postcode', 'city', 'state']

class DonationSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    location = LocationSerializer()
    class Meta:
        model = Donation
        fields = '__all__'

class DonationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationRecord
        fields = ['id', 'donation', 'quantity', 'user', 'date']
        read_only_fields = ['user', 'date']

    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise AuthenticationFailed("User is inactive.")
                update_last_login(None, user)
                data['user'] = user
            else:
                raise AuthenticationFailed("Invalid credentials.")
        else:
            raise serializers.ValidationError("Must include username and password.")

        return data

class DonationHistorySerializer(serializers.ModelSerializer):
    donation = DonationSerializer(read_only=True)  
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = DonationHistory
        fields = ['id','user_id', 'user', 'donation', 'quantity', 'date']
        
class ShelterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shelter
        fields = '__all__'

class WaterLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterLevel
        fields = '__all__'