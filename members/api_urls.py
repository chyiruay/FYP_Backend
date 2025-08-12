# members/api_urls.py
from django.urls import path
from .api_views import (
    RegisterView,  LoginView, UserListView, DonationListView, DonationRecordView, 
    BanjirStateAPIView, StateListView, WaterLevelAPI, DonationHistoryView, UpdateProfileView, ChangePasswordView,
    ShelterListAPIView
    )
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api-register'),
    path('login/', LoginView.as_view(), name='api-login'),
    path('users/', UserListView.as_view(), name='api-user-list'),
    path('update_profile/', UpdateProfileView.as_view(), name='update-profile'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('donations/', DonationListView.as_view(), name='api-donations'),
    path('donation-records/', DonationRecordView.as_view(), name='api-donation-records'),
    path('shelters/', ShelterListAPIView.as_view(), name='shelter-list'),
    path('water-level/', WaterLevelAPI.as_view(), name='water-level'),
    path("banjir/", BanjirStateAPIView.as_view(), name="banjir_api"),
    path("states/", StateListView.as_view(), name="state_list"),
    path('api-token-auth/', obtain_auth_token),
    path('donation-history/', DonationHistoryView.as_view(), name='donation_history'),
]
