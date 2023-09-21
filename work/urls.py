from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new-work", views.new_work, name="new-work"),
]