from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.loginUser, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerUser, name="register"),

    path('', views.profiles, name="profiles"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),
    path('account/', views.userAccount, name="user-account"),
    path('inbox/', views.inbox, name="user-inbox"),
    path('message/<str:pk>/', views.readMessage, name="message"),
    path('send-message/<str:pk>/', views.sendMessage, name="send-message"),
    path('update-profile/', views.updateProfile, name="update-profile"),
    path('add-skill/', views.addSkill, name="add-skill"),
    path('update-skill/<str:pk>/', views.updateSkill, name="update-skill"),
    path('delete-skill/<str:pk>/', views.deleteSkill, name="delete-skill"),
]