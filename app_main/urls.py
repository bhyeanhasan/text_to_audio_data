from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload_data/', views.upload_data, name='upload_data'),
    path('statistics/', views.statistics, name='statistics'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
]
