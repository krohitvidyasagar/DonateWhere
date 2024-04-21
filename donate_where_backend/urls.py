"""
URL configuration for donate_where_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from donation.views import UserRegistrationView, LoginView, ProfileView, DonationListCreateView, \
    DonationRetrievePutDeleteView, DonationClaimView, ClaimListView

urlpatterns = [
    # API to register new users
    path('api/register', UserRegistrationView.as_view(), name=UserRegistrationView.name),
    # API to login
    path('api/login', LoginView.as_view(), name=LoginView.name),
    # API for profile
    path('api/profile', ProfileView.as_view(), name=ProfileView.name),

    # API to list and create donations
    path('api/donation', DonationListCreateView.as_view(), name=DonationListCreateView.name),
    # API to retrieve, update and delete donation
    path('api/donation/<uuid:pk>', DonationRetrievePutDeleteView.as_view(),
         name=DonationRetrievePutDeleteView.name),

    # API to list all claims
    path('api/claim', ClaimListView.as_view(), name=ClaimListView.name),
    # API to reserve a donation or delete a claim
    path('api/donation/<uuid:pk>/claim', DonationClaimView.as_view(), name=DonationClaimView.name),

]
