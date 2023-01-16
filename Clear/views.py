
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import UpdateView, CreateView
from Clear.forms import RegisterForm, SettingsForm
from Clear.models import AppUser, UserInhaler, Inhalers, Boroughs, PollutionLevels
from django.shortcuts import get_object_or_404
# from django.views import View
from django.views.generic import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import redirect
from django.contrib import messages
from ClearWeb.settings import AUTH_USER_MODEL
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg, Count

import json


# Create view for register page
class RegisterView(CreateView):
    # Setting the model for the create view to be the AppUser database (assigned to AUTH_USER_MODEL in settings.py)
    model = AUTH_USER_MODEL
    # Use our custom RegisterForm in order to add our additional user profile fields and ensure appropriate widgets are used
    form_class = RegisterForm
    template_name = 'clear/registration/register.html'
    success_url = reverse_lazy('login')


# Create view for inhaler log page
class UserInhalerView(LoginRequiredMixin, ListView):
    # The LoginRequiredMixin parameter is a Django mixin which ensures the user must be logged in to access this view
    # Filter the UserInhaler model to only the logged in user's inhalers
    def get_queryset(self):
        qs = UserInhaler.objects.filter(user_id=self.request.user.id)
        return qs
    model = UserInhaler
    template_name = 'clear/main/inhaler.html'
    login_url = '/login/'


# Create view for the pollution page using Django class based views and the login mixin
class PollutionView(LoginRequiredMixin, TemplateView):
    # Set the loaded template to pollution.html
    template_name = 'clear/main/pollution.html'
    # If the user attempts to access this page without being logged in, redirect to the login page
    login_url = '/login/'

    # Define additional contextual data to be provided to the view
    def get_context_data(self, **kwargs):
        # Retrieve the object of the current user
        current_user = self.request.user
        # Load default context data
        context = super().get_context_data(**kwargs)
        # Add context property to provide list of Boroughs for the template
        context['borough_choices'] = Boroughs.objects.all()
        # Load our user with the related boroughs so that we can display them on the Current Levels cards
        context['user_boroughs'] = get_user_model().objects.select_related("current_borough","home_borough","work_borough","other_borough").get(pk=current_user.id)
        # Use an aggregate query to calculate the top 5 best boroughs by average pollution level for all time
        context['top5_boroughs'] = Boroughs.objects.filter(borough_pollution__isnull = False).annotate(average_pollution=Avg('borough_pollution__pollution_level')).order_by('average_pollution')[:5]
        # Use an aggregate query to calculate the 5 worst boroughs based on current pollution level
        context['current_worst5_boroughs'] = PollutionLevels.objects.select_related("borough").filter(current_flag=1).order_by('-pollution_level')[:5]

        # Load the current PollutionLevels model for the related Boroughs
        context['current_borough_levels'] = PollutionLevels.objects.filter(current_flag=1, borough_id=current_user.current_borough_id).first()
        context['home_borough_levels'] = PollutionLevels.objects.filter(current_flag=1, borough_id=current_user.home_borough_id).first()
        context['work_borough_levels'] = PollutionLevels.objects.filter(current_flag=1, borough_id=current_user.work_borough_id).first()
        context['other_borough_levels'] = PollutionLevels.objects.filter(current_flag=1, borough_id=current_user.other_borough_id).first()
        return context


class SettingsView(LoginRequiredMixin, UpdateView):
    template_name = 'clear/main/settings.html'
    user_form = SettingsForm
    login_url = '/login/'
    def get(self, request):
        user = get_object_or_404(AppUser, id = request.user.id)
        inhalers = UserInhaler.objects.filter(user_id = user.id)
        user_form = self.user_form(instance = user)
        return render(request, self.template_name, context= {"form":user_form,"inhalers":inhalers})

    def post(self,request):
        print("post inside")
        user = get_object_or_404(AppUser, id = request.user.id)
        form_class = SettingsForm(request.POST,instance = user)
        if form_class.is_valid():
            print(request.POST)
            form_class.save()
            inhaler_id = request.POST.getlist('inhaler_id')
            print("POST inhaler_id:", inhaler_id)
            inhaler_type = request.POST.getlist('inhaler_type')
            print("POST inhaler_type:", inhaler_type)
            puff_remaining = request.POST.getlist('puff_remaining')
            puffs = request.POST.getlist('puffs')
            per_day = request.POST.getlist('per_day')
            if inhaler_type and puff_remaining and per_day:
                print("POST inside:")
                all_user_inhalers = [{
                    'inhaler_id': inhaler_id,
                    "type": type,
                    "puff_remaining": puff_remaining,
                    "per_day": per_day,
                }
                    for inhaler_id, type, puff_remaining, per_day in
                    zip(inhaler_id, inhaler_type, puff_remaining, per_day)]
                for i in all_user_inhalers:
                    obj = get_object_or_404(UserInhaler, id=i['inhaler_id'])
                    obj.inhaler_type = i['type']
                    obj.puffs_per_day = i['per_day']
                    obj.puffs_remaining = i['puff_remaining']
                    obj.save()
                messages.warning(request, 'User settings has been updated successfully')
                return redirect('settings')
            messages.warning(request, 'User settings has been updated successfully')
            return redirect('settings')

        else:
            messages.error(request, 'Please fill in all required fields')
            return redirect('settings')


def BoroughView(request):
    data = PollutionLevels.get_borough_map()
    json_data = json.loads(data)
    return JsonResponse(json_data)


def getIDfromInhalerType(inhaler_type):
    inhaler_name = ""
    if (inhaler_type == "Beclametasone_dipropionate"):
        inhaler_name = "Beclametasone Dipropionate"
    elif (inhaler_type == "Ciclesonide"):
        inhaler_name = "Ciclesonide"
    elif (inhaler_type == "Fluticasone_poprionate"):
        inhaler_name = "Fluticasone Poprionate"
    elif (inhaler_type == "Beclometasone"):
        inhaler_name = "Beclometasone"
    elif (inhaler_type == "Budesonide"):
        inhaler_name = "Budesonide"
    elif (inhaler_type == "Fluticasone_poprionate"):
        inhaler_name = "Fluticasone Poprionate"
    elif (inhaler_type == "Mometasone"):
        inhaler_name = "Mometasone"
    elif (inhaler_type == "Beclometasone_dipropionate_with_ormoterol"):
        inhaler_name = "Beclometasone Dipropionate with Ormoterol"
    elif (inhaler_type == "Budesonide_with_formoterol"):
        inhaler_name = "Budesonide with Formoterol"
    elif (inhaler_type == "Fluticasone_poprionate_with_formoterol"):
        inhaler_name = "Fluticasone Poprionate with Formoterol"
    elif (inhaler_type == "Fluticasone_poprionate_with_salmeterol"):
        inhaler_name = "Fluticasone Poprionate with Salmeterol"
    elif (inhaler_type == "Fluticasone_poprionate_with_vilanterol"):
        inhaler_name = "Fluticasone Furoate with Vilanterol"

    inhaler_ids = Inhalers.objects.filter(name=inhaler_name)
    for id in inhaler_ids:
        print(id)
    inhaler_id = str(inhaler_ids[0].id)
    return inhaler_id
def add_inhaler(request):
    print(add_inhaler)
    user_id = request.user.id
    inhaler_type = request.POST.get('inhaler_type')
    inhaler_id = getIDfromInhalerType(inhaler_type)
    print(inhaler_id)

    puff_remaining = request.POST.get('Puffs_Remaining')
    per_day = request.POST.get('Per_Day')

    if inhaler_id and puff_remaining and per_day:
        obj = UserInhaler.objects.create(
            user_id=user_id,
            inhaler_id=inhaler_id,
            puffs_remaining=puff_remaining,
            puffs_per_day=per_day,
        )
        obj.save()
        messages.success(request, 'Inhaler has been added successfully')
        return redirect('settings')

    messages.error(request, 'Please fill in all required fields')
    return redirect('settings')
def delete_inhaler(request, *args, **kwargs):
    id = kwargs.get('id')
    obj = get_object_or_404(UserInhaler, id=id)
    obj.delete()
    messages.warning(request, "Inhaler has been deleted successfully.")
    return redirect("settings")


def logInhalerPuff(request, user_inhaler_id):
    # Allow user to log puff while the inhaler has > 0 puffs remaining
    if UserInhaler.log_puff(user_inhaler_id) is not None:
        return redirect(reverse_lazy('inhalers'))
    return redirect("inhalers")


def logCurrentLocation(request, borough_id):
    # Gets the logged-in user
    current_user = request.user
    # Calls the set current borough method in the AppUser model passing the current user object and borough id
    AppUser.set_new_current_borough(current_user, borough_id)
    # Returns the user to the pollution page
    return redirect(reverse_lazy('pollution'))


def updatePollutionLevels(request):
    # Call the function to update pollution levels in the pollution level table
    PollutionLevels.update_pollution_levels()
    return HttpResponse("OK")
