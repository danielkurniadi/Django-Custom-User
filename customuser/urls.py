from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from users.views import redirect_login

urlpatterns = [
    path('', redirect_login),
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('duties/', include('duty_api.urls')),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
