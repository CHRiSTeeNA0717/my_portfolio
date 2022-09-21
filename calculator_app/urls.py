from atexit import register
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/',views.login, name='login'),
    path('index/', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('newinput/', views.newinput, name='newinput'),
    path('history/', views.history, name='history'),
    path('roominput/', views.roominput, name='roominput'),
    path('contact/', views.contact, name='contact'),
    path('manual/', views.manual, name='manual'),
    path('guest/',views.guest, name='guest')
]