from django.urls import path
from django.contrib.auth import views as authviews

from .views import *

urlpatterns = [
	path('login/', authviews.LoginView.as_view(), name='login'),
	path('logout/', authviews.LogoutView.as_view(), name='logout'),
	path('register/', RegisterView.as_view(), name='register'),
]
