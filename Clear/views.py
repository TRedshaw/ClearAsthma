
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
from django.http import JsonResponse
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import redirect
from django.contrib import messages
from ClearWeb.settings import AUTH_USER_MODEL


# Create your views here.
class RegisterView(CreateView):
    # Create view for register page
    model = AUTH_USER_MODEL
    form_class = RegisterForm
    template_name = 'clear/registration/register.html'
    success_url = reverse_lazy('login')


class UserInhalerView(LoginRequiredMixin, ListView):
    # Get the
    def get_queryset(self):
        qs = UserInhaler.objects.filter(user_id=self.request.user.id)
        return qs
    model = UserInhaler
    template_name = 'clear/main/inhaler.html'
    login_url = '/clear/login/'


# TODO Add context data here
class PollutionView(LoginRequiredMixin, TemplateView):
    template_name = 'clear/main/pollution.html'
    login_url = '/clear/login/'

    def get_context_data(self, request, **kwargs):
        current_user = request.user
        context = super().get_context_data(**kwargs)
        context['borough_choices'] = Boroughs.objects.all()
        context['current_borough_levels'] = PollutionLevels.objects.get(id=current_user.current_borough_id)
        context['home_borough_levels'] = PollutionLevels.objects.get(id=current_user.home_borough_id)
        context['work_borough_levels'] = PollutionLevels.objects.get(id=current_user.work_borough_id)
        context['other_borough_levels'] = PollutionLevels.objects.get(id=current_user.other_borough_id)
        return context

# TODO @Anna -  Finish the code for this view section - need to change the tempalte view
class SettingsView(LoginRequiredMixin, UpdateView):
    template_name = 'clear/main/settings.html'
    user_form = SettingsForm
    login_url = '/clear/login/'
    def get(self, request):
        user = get_object_or_404(AppUser, id = request.user.id)
        inhalers = Inhalers.objects.filter(user = request.user)
        user_form = self.user_form(instance = user)
        return render(request, self.template_name, context= {"form":user_form,"inhalers":inhalers})

    def post(self,request):
        user = get_object_or_404(AppUser, id = request.user.id)
        form_class = SettingsForm(request.POST,instance = user)
        if form_class.is_valid():
            print("")
            form_class.save()
            inhaler_id = request.POST.getlist('inhaler_id')
            inhaler_type = request.POST.getlist('inhaler_type')
            puff_remaining = request.POST.getlist('puff_remaining')
            puffs = request.POST.getlist('puffs')
            per_day = request.POST.getlist('per_day')
            if inhaler_type and puff_remaining and per_day:
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


def add_inhaler(request):
    user = request.user
    inhaler_type = request.POST.get('inhaler_type')
    puff_remaining = request.POST.get('Puffs_Remaining')
    per_day = request.POST.get('Per_Day')
    if inhaler_type and puff_remaining and per_day:
        obj = UserInhaler.objects.create(
            user_id=user,
            inhaler_type=inhaler_type,
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
    if UserInhaler.log_puff(user_inhaler_id) is not None:
        return redirect(reverse_lazy('inhalers'))
    #messages.warning(request,"Inhaler cannot be logged any more.")
    return redirect("inhalers")


def logCurrentLocation(request, borough_id):
    current_user = request.user
    AppUser.set_new_current_borough(current_user, borough_id)
    return redirect(reverse_lazy('pollution'))

