from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic.detail import DetailView
from .forms import SignUpForm

def redirect_login(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('users:profile')
        return redirect('/accounts/login/')

class UserView(DetailView):
    template_name = 'profile.html'

    def get_object(self, queryset=None):
        return self.request.user

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, email=user.email, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('users:profile')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
