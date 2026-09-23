from django.urls import path
from django.views.generic import TemplateView
from .views import *

urlpatterns = [
	path('', TemplateView.as_view(template_name="hats/frontpage.html"), name="frontpage"),
	path('my-data/', MyDataView.as_view(), name="my-data"),
	path('admin-dashboard/', AdminDashboardView.as_view(), name="admin-dashboard"),
	path('admin-console/', AdminShowAllView.as_view(), name="admin-console"),
]
