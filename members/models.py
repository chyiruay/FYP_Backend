from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

# User
class CustomUser(AbstractUser):
    house_number = models.CharField(max_length=20, blank=True, null=True)
    street_name = models.CharField(max_length=100, blank=True, null=True)
    residential_area = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)

    def full_address(self):
        parts = [
            self.house_number,
            self.street_name,
            self.residential_area,
            self.postcode,
            self.city,
            self.state
        ]
        # Skip empty or None fields
        return ', '.join([part for part in parts if part])

    phone_number = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')], blank=True)
    is_employee = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    def __str__(self):
      return self.username
    
# Category  
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
# Location
class Location(models.Model):
    house_number = models.CharField(max_length=10)
    street_name = models.CharField(max_length=100)
    residential_area = models.CharField(max_length=100) 
    postcode = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.house_number}, {self.street_name}, {self.residential_area}, {self.postcode}, {self.city}, {self.state}"

# Donation
class Donation(models.Model):
    donationName = models.CharField(max_length=100)
    donationQuantity = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.donationName}"


class DonationRecord(models.Model):
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

class DonationHistory(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} donated {self.quantity} of {self.donation.donationName} on {self.date}"

# Shelter
class Shelter(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    available = models.BooleanField(default=True)
    address = models.TextField(blank=True, null=True)
    capacity = models.IntegerField(default=0)
    has_water = models.BooleanField(default=False)
    has_food = models.BooleanField(default=False)
    is_accessible = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

# Water level
class WaterLevel(models.Model):
    station_id = models.CharField(max_length=20)
    station_name = models.CharField(max_length=200)
    district = models.CharField(max_length=100)
    main_basin = models.CharField(max_length=100)
    sub_basin = models.CharField(max_length=100)
    last_update = models.CharField(max_length=100)
    water_level = models.CharField(max_length=10)
    normal = models.CharField(max_length=10)
    alert = models.CharField(max_length=10)
    warning = models.CharField(max_length=10)
    danger = models.CharField(max_length=10)
    state_code = models.CharField(max_length=10)
    