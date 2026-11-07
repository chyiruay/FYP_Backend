from django import forms
from .models import Donation, DonationRecord, CustomUser, Category, Location, Shelter
from django.contrib.auth.forms import UserCreationForm

# User registration form (uses CustomUser)
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email','phone_number', 'gender', 'password1', 'password2')

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'gender', 'house_number', 'street_name', 'residential_area', 'postcode', 'city', 'state']
        labels = {
            'username': 'Username',
            'email': 'Email',
            'phone_number': 'Phone Number',
            'gender': 'Gender',
            'house_number': 'House Number',
            'street_name': 'Street Name',
            'residential_area': 'Residential Area',
            'postcode': 'Postcode',
            'city': 'City',
            'state': 'State',
        }

# Donation
class DonationRecordForm(forms.ModelForm):
    class Meta:
        model = DonationRecord
        fields = ['donation', 'quantity']

    def clean(self):
        cleaned_data = super().clean()
        donation = cleaned_data.get('donation')
        quantity = cleaned_data.get('quantity')

        if donation and quantity and quantity > int(donation.donationQuantity):
            self.add_error('quantity', 'Quantity cannot exceed available donation quantity.')

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['donationName', 'donationQuantity', 'category', 'location']
        labels = {
            'donationName': 'Donation Name',
            'donationQuantity': 'Donation Quantity',
            'category': 'Category',
            'location': 'Location',
        }

class DonationEditForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['donationName', 'donationQuantity', 'category', 'location']
        labels = {
            'donationName': 'Donation Name',
            'donationQuantity': 'Donation Quantity',
            'category': 'Category',
            'location': 'Location',
        }

# Category
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {
            'name': 'Category Name',
        }

class CategoryEditForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {
            'name': 'Category Name',
        }
#Location
class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['house_number', 'street_name', 'residential_area', 'postcode', 'city', 'state']
        labels = {
            'house_number': 'House Number',
            'street_name': 'Street Name',
            'residential_area': 'Residential Area',
            'postcode': 'Postcode',
            'city': 'City',
            'state': 'State',
        }

class LocationEditForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['house_number', 'street_name', 'residential_area', 'postcode', 'city', 'state']
        labels = {
            'house_number': 'House Number',
            'street_name': 'Street Name',
            'residential_area': 'Residential Area',
            'postcode': 'Postcode',
            'city': 'City',
            'state': 'State',
        }

#shelter
class ShelterForm(forms.ModelForm):
    class Meta:
        model = Shelter
        fields = ['name', 'latitude', 'longitude', 'available', 'address', 'capacity', 'has_water', 'has_food', 'is_accessible', 'notes']
        labels = {
            'name': 'Shelter Name',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
            'available': 'Available',
            'address': 'Address',
            'capacity': 'Capacity',
            'has_water': 'Has Water',
            'has_food': 'Has Food',
            'is_accessible': 'Is Accessible',
            'notes': 'Note',
        }

class ShelterEditForm(forms.ModelForm):
    class Meta:
        model = Shelter
        fields = ['name', 'latitude', 'longitude', 'available', 'address', 'capacity', 'has_water', 'has_food', 'is_accessible', 'notes']
        labels = {
            'name': 'Shelter Name',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
            'available': 'Available',
            'address': 'Address',
            'capacity': 'Capacity',
            'has_water': 'Has Water',
            'has_food': 'Has Food',
            'is_accessible': 'Is Accessible',
            'notes': 'Note',
        }