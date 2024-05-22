from django.urls import path

from . import views
from .views import test_view

urlpatterns = [
    # path("", views.index, name="index"),
    path('test/', test_view, name='test_view'),
]