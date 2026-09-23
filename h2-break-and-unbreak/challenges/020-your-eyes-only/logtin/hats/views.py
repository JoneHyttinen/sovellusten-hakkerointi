from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin

class MyDataView(UserPassesTestMixin, TemplateView):
	template_name="hats/my-data.html"

	def test_func(self):
		return self.request.user.is_authenticated

class AdminDashboardView(UserPassesTestMixin, TemplateView):
	template_name="hats/admin-show-all.html"

	def test_func(self):
		return self.request.user.is_authenticated and self.request.user.is_staff

class AdminShowAllView(UserPassesTestMixin, TemplateView):
	template_name="hats/admin-show-all.html"

	def test_func(self):
		return self.request.user.is_authenticated
