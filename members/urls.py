from django.urls import path
from . import views
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    #捐赠路径
    path("", views.donation_list, name="donation"),
    path('donations/new/', views.donate_create, name='donate_create_empty'),
    path('donations/new/<int:donation_id>/', views.donate_create, name='donate_create'),
    path('donations/add/', views.add_donation, name='add_donation'), 
    path('donation/edit/<int:donation_id>/', views.edit_donation, name='edit_donation'),
    path('delete_donation/<int:id>/', views.delete_donation, name='delete_donation'),
    path('history/', views.donation_history, name='history'),
    #分类路径
    path('category/', views.category_view, name='category'),
    path('category/add/', views.add_category, name='add_category'),
    path('category/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:id>/', views.delete_category, name='delete_category'),
    #地点路径
    path('location/', views.location_view, name='location'),
    path('location/add/', views.add_location, name='add_location'),
    path('location/edit/<int:location_id>/', views.edit_location, name='edit_location'),
    path('delete_location/<int:id>/', views.delete_location, name='delete_location'),
    #避难所路径
    path('shelter/', views.shelter_view, name='shelter'),
    path('shelter/add/', views.add_shelter, name='add_shelter'),
    path('shelter/edit/<int:shelter_id>/', views.edit_shelter, name='edit_shelter'),
    path('delete_shelter/<int:id>/', views.delete_shelter, name='delete_shelter'),
    #用户路径
    path("main/", views.user_list, name="users"),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/password/', views.change_password_view, name='change_password_profile'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete_user/<int:id>/', views.delete_user, name='delete_user'),


    path("accounts/", include([
        path("", include("accounts.urls")),
        path("", include("django.contrib.auth.urls")),
    ])),

    path('api/', include('members.api_urls')),
]
