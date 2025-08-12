# members/api_views.py
from rest_framework import generics, permissions, status
from .models import Donation, DonationRecord, CustomUser, DonationHistory, Shelter
from rest_framework.response import Response
from .serializers import (
    DonationSerializer, DonationRecordSerializer, RegisterSerializer, CustomUserSerializer, LoginSerializer,
    DonationRecordSerializer, DonationHistory, DonationHistorySerializer, WaterLevelSerializer, UserEditSerializer, ShelterSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .banjir_api import scrape_state_banjir_data
import json
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import update_last_login

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        token = Token.objects.create(user=user)
        self.token = token.key  # 将token传递给response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if hasattr(self, 'token'):
            response.data['token'] = self.token
        return response

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer  # 指定序列化器
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)  # 使用父类方法
        serializer.is_valid(raise_exception=True)  # 自动返回400错误
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "message": "Login successful",
            "email": user.email,
            "username": user.username,
            "phone_number": user.phone_number,
            "gender": user.gender,
            "house_number": user.house_number,
            "street_name": user.street_name,
            "residential_area": user.residential_area,
            "postcode": user.postcode,
            "city": user.city,
            "state": user.state,
            "is_employee": user.is_employee if hasattr(user, 'is_employee') else False,
            "full_address": user.full_address() 
        })

class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAdminUser] 

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully'})
        return Response(serializer.errors, status=400)

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({"error": "Old and new passwords are required."}, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(old_password, user.password):
            return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 6:
            return Response({"error": "New password must be at least 6 characters."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        update_last_login(None, user)

        return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)


class DonationListView(generics.ListCreateAPIView):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer

class DonationRecordView(APIView):
    def post(self, request):
        serializer = DonationRecordSerializer(data=request.data)
        if serializer.is_valid():
            donation_id = serializer.validated_data['donation'].id
            quantity_donated = serializer.validated_data['quantity']
            
            try:
                donation = Donation.objects.get(id=donation_id)
                if quantity_donated > donation.donationQuantity:
                    return Response({'error': 'Donated quantity exceeds available amount'}, status=400)
                
                serializer.save(user = request.user)

                DonationHistory.objects.create(
                    user=request.user,
                    donation=donation,
                    quantity=quantity_donated
                )

                donation.donationQuantity -= quantity_donated
                if donation.donationQuantity == 0:
                    donation.delete()
                else:
                    donation.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Donation.DoesNotExist:
                return Response({'error': 'Donation not found'}, status=404)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BanjirStateAPIView(APIView):
    def get(self, request):
        state = request.GET.get('state')
        if not state:
            return Response({"error": "State parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = scrape_state_banjir_data(state)
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StateListView(APIView):
    def get(self, request):
        states = [
            {"code": "JHR", "name": "Johor"},
            {"code": "KDH", "name": "Kedah"},
            {"code": "KTN", "name": "Kelantan"},
            {"code": "MLK", "name": "Melaka"},
            {"code": "NSN", "name": "Negeri Sembilan"},
            {"code": "PHG", "name": "Pahang"},
            {"code": "PRK", "name": "Perak"},
            {"code": "PLS", "name": "Perlis"},
            {"code": "PNG", "name": "Pulau Pinang"},
            {"code": "SBH", "name": "Sabah"},
            {"code": "SWK", "name": "Sarawak"},
            {"code": "SGR", "name": "Selangor"},
            {"code": "TRG", "name": "Terengganu"},
            {"code": "KUL", "name": "Kuala Lumpur"},
            {"code": "LBN", "name": "Labuan"},
            {"code": "PJY", "name": "Putrajaya"},
        ]
        return Response(states)

class WaterLevelAPI(APIView):
    def get(self, request):
        state = request.GET.get("state")
        if not state:
            return Response({"error": "state is required"}, status=400)

        try:
            with open("data/banjir_data.json", "r", encoding="utf-8") as f:
                all_data = json.load(f)
            filtered_data = [entry for entry in all_data if entry.get("state_code") == state]
            return Response(filtered_data)
        except FileNotFoundError:
            return Response({"error": "Data file not found."}, status=500)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class DonationHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = DonationHistory.objects.filter(user=request.user).order_by('-date')
        serializer = DonationHistorySerializer(history, many=True)
        return Response(serializer.data)
    
class ShelterListAPIView(generics.ListAPIView):
    queryset = Shelter.objects.all()
    serializer_class = ShelterSerializer
    permission_classes = [AllowAny]
