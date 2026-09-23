# Copyright 2024 Tero Karvinen https://TeroKarvinen.com

from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.urls import reverse

class RegisterForm(UserCreationForm):
	class Meta(UserCreationForm.Meta):
		model = User
		fields = UserCreationForm.Meta.fields

class RegisterView(CreateView):
	form_class = RegisterForm
	template_name = "registration/register.html"
	#success_url = "/"

	def get_success_url(self, **kwargs):
		return reverse("login")
