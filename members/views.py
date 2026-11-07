from django.http import HttpResponse
from django.template import loader
from .models import Donation, CustomUser, Category, Location, DonationHistory, Shelter
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import (DonationRecordForm, DonationForm, CustomUserCreationForm,DonationEditForm, 
                    CategoryForm, UserEditForm, CategoryEditForm, LocationForm, LocationEditForm,ShelterForm, ShelterEditForm)
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from urllib.parse import urlencode
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.admin.views.decorators import staff_member_required


# Donation views
def donation_list(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    state = request.GET.get('state')
    city = request.GET.get('city')

    donations = Donation.objects.select_related('location', 'category').all()

    if query:
        donations = donations.filter(
            Q(id__iexact=query) |
            Q(donationName__icontains=query)
        )

    if category_id:
        donations = donations.filter(category__id=category_id)

    if state:
        donations = donations.filter(location__state=state)

    if city:
        donations = donations.filter(location__city=city)

    categories = Category.objects.all()
    states = Location.objects.values_list('state', flat=True).distinct()
    cities = Location.objects.values_list('city', flat=True).distinct()

    context = {
        'donations': donations,
        'categories': categories,
        'states': states,
        'cities': cities,
        'selected_category': category_id,
        'selected_state': state,
        'selected_city': city,
        'query': query,  
    }
    return render(request, 'donation/donation.html', context)

@staff_member_required
def donate_create(request, donation_id=None):
    if request.method == 'POST':
        form = DonationRecordForm(request.POST)
        if form.is_valid():
            donation_record = form.save(commit=False)
            donation = donation_record.donation

            # Decrease stock
            donation.donationQuantity -= int(donation_record.quantity)
            donation.save()

            donation_record.save()
            return redirect('donation')
    else:
        if donation_id:
            form = DonationRecordForm(initial={'donation': donation_id})
        else:
            form = DonationRecordForm()
    return render(request, 'donation/donation_form.html', {'form': form})

@staff_member_required
def add_donation(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('donation')  
    else:
        form = DonationForm()
    return render(request, 'donation/add_donation.html', {'form': form})

@staff_member_required
def edit_donation(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    category = request.GET.get('category', '')
    if request.method == 'POST':
        form = DonationEditForm(request.POST, instance=donation)
        if form.is_valid():
            form.save()
            redirect_url = reverse('donation')
            if category:
                redirect_url += '?' + urlencode({'category': category})
            return HttpResponseRedirect(redirect_url)
    else:
        form = DonationEditForm(instance=donation)

    return render(request, 'donation/edit_donation.html', {
        'form': form,
        'category': category  
    })
@staff_member_required
def delete_donation(request, id):
  
    donation = Donation.objects.get(id=id)
    donation.delete()
    return redirect('donation') 

def donation_history(request):
    query = request.GET.get('q') 

    if query:
        historys =DonationHistory.objects.filter(
            Q(id__iexact=query) | 
            Q(user__username__icontains=query) |
            Q(donation__donationName__icontains=query)
        )
    else:
        historys = DonationHistory.objects.all()

    return render(request, 'donation/donation_history.html', {
        'historys': historys,
        'query': query,  
    })

# Category views
def category_view(request):
    query = request.GET.get('q') 

    if query:
        categorys =Category.objects.filter(
            Q(id__iexact=query) | 
            Q(name__icontains=query) 
        )
    else:
        categorys = Category.objects.all()

    return render(request, 'category/category.html', {
        'categorys': categorys,
        'query': query,  
    })

@staff_member_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category')  
    else:
        form = CategoryForm()
    return render(request, 'category/add_category.html', {'form': form})

@staff_member_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryEditForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category')
    else:
        form = CategoryEditForm(instance=category)

    return render(request, 'category/edit_category.html', {'form': form,})

@staff_member_required
def delete_category(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    return redirect('category') 

# Location views
def location_view(request):
    query = request.GET.get('q') 

    if query:
        locations = Location.objects.filter(
            Q(id__iexact=query) |  
            Q(house_number__iexact=query) |
            Q(street_name__icontains=query) |   
            Q(residential_area__icontains=query) |
            Q(postcode__iexact=query) |
            Q(city__icontains=query) |
            Q(state__icontains=query)
        )
    else:
        locations = Location.objects.all()

    return render(request, 'location/location.html', {
        'locations': locations,
        'query': query,  
    })

@staff_member_required
def add_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('location')  
    else:
        form = LocationForm()
    return render(request, 'location/add_location.html', {'form': form})

@staff_member_required
def edit_location(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    if request.method == 'POST':
        form = LocationEditForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return redirect('location')
    else:
        form = LocationEditForm(instance=location)

    return render(request, 'location/edit_location.html', {'form': form,})

@staff_member_required
def delete_location(request, id):
    location = Location.objects.get(id=id)
    location.delete()
    return redirect('location') 

#shelter
def shelter_view(request):
    query = request.GET.get('q') 

    if query:
        shelters = Shelter.objects.filter(
            Q(id__iexact=query) |  # exact ID match
            Q(name__icontains=query)  # partial name match  
        )
    else:
        shelters = Shelter.objects.all()

    return render(request, 'shelter/shelter.html', {
        'shelters': shelters,
        'query': query,  
    })

@staff_member_required
def add_shelter(request):
    if request.method == 'POST':
        form = ShelterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shelter')  
    else:
        form = ShelterForm()
    return render(request, 'shelter/add_shelter.html', {'form': form})

@staff_member_required
def edit_shelter(request, shelter_id):
    shelter = get_object_or_404(Shelter, id=shelter_id)
    if request.method == 'POST':
        form = ShelterEditForm(request.POST, instance=shelter)
        if form.is_valid():
            form.save()
            return redirect('shelter')
    else:
        form = ShelterEditForm(instance=shelter)

    return render(request, 'shelter/edit_shelter.html', {'form': form,})

@staff_member_required
def delete_shelter(request, id):
    shelter = Shelter.objects.get(id=id)
    shelter.delete()
    return redirect('shelter') 

# User views
def user_list(request):
    query = request.GET.get('q') 

    if query:
        myusers = CustomUser.objects.filter(
            Q(id__iexact=query) |  
            Q(username__icontains=query) 
        )
    else:
        myusers = CustomUser.objects.all()

    return render(request, 'user/user.html', {
        'myusers': myusers,
        'query': query, 
        })

def authView(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  
            user.is_employee = True        
            user.is_staff = True 
            user.save()                    
            return redirect('login')  
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def profile_view(request):
    return render(request, 'user/profile.html', {'user': request.user})

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'user/edit_profile.html', {'form': form})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'user/password.html', {'form': form})

@staff_member_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users')  
    else:
        form = UserEditForm(instance=user)
    return render(request, 'user/edit_user.html', {'form': form, 'edit_user': user})


@login_required
def delete_user(request, id):
    user = get_object_or_404(CustomUser, id=id)
    user.delete()
    return redirect('users')


