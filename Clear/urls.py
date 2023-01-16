"""ClearWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from . import views
from django.contrib.auth import views as auth_views

from .forms import LoginForm

urlpatterns = [
    # See this link for class-based views documentation
    # https://docs.djangoproject.com/en/4.1/topics/class-based-views/intro/
    path('register/', views.RegisterView.as_view(), name='register'),
    # Login view
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form=LoginForm), name='login'),
    # Logout view
    path('logout/', auth_views.LogoutView.as_view(template_name='auth/logout.html'), name='logout'),
    # Password reset view
    path('password_reset', auth_views.PasswordChangeView.as_view(), name='password_reset'),

    # Custom User Inhalers list view route
    path('inhalers/', views.UserInhalerView.as_view(), name='inhalers'),
    # URL to log puff calling appropriate function
    path('inhaler/log_puff/<int:user_inhaler_id>', views.logInhalerPuff, name='inhaler_log_puff'),
    # Update pollution levels from the Air Quality API
    path('pollution_levels/update/', views.updatePollutionLevels, name='update_pollution_levels'),
    # Custom Pollution Info view
    path('pollution/', views.PollutionView.as_view(), name='pollution'),
    #get the returned updated JSON variable from get_borough_map()
    path('getboroughdata/', views.BoroughView, name='getboroughdata'),


    # Set current location to a Borough
    path('pollution/set_current_location/<int:borough_id>', views.logCurrentLocation, name='pollution_log_location'),
    # Edit settings (custom UpdateView)
    path('settings/', views.SettingsView.as_view(), name='settings'),
    # Add User Inhaler view
    path('add_inhaler/', views.add_inhaler, name='add_inhaler'),
    # Delete User Inhaler view
    path('delete_inhaler/<int:id>/',views.delete_inhaler,name="delete_inhaler")
]
