from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from .views import UserView, signup

app_name = 'users'

urlpatterns = [
    path('profile/', login_required(UserView.as_view()), name='profile'),
    path('signup/', signup, name='signup'),
    path('login/',  
        auth_views.LoginView.as_view(
            template_name='login.html', 
            redirect_authenticated_user=True), 
        name='login'
    ),
]
