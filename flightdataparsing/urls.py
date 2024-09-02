from django.urls import path
from . import views

urlpatterns = [
    path("",views.displayingFlights, name="displayTable"),
]