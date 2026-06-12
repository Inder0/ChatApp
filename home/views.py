from django.shortcuts import redirect, render
from django.views.generic import TemplateView

# Create your views here.

class HomeView(TemplateView):
    template_name='base.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if profile and not profile.onboarding_completed:
                return redirect("profile-onboarding")
        return super().dispatch(request, *args, **kwargs)
