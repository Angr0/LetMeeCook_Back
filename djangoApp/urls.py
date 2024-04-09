"""
URL configuration for djangoApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from let_me_cook import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', views.manageUsers),
    path('login/', views.loginUser),
    path('recipes/', views.recipes),
    path('recipe/<str:recipe_name>/', views.recipe),
    path('cooking-history/<str:user_login>/', views.cookingHistory),
    path('cooking-history/', views.cookingHistory),
    path('fridge/<str:user_login>/', views.fridge),
    path('bio-calc/<str:user_login>/', views.userBmi),
    path('user-data/<str:user_login>/', views.userData),
    path('favourite-recipes/<str:user_login>/', views.favouriteRecipes),
    path('categories/', views.categories),
    path('flavours/', views.flavours),
    path('all-ingredients/', views.allIngredients),
    path('ingredients/', views.ingredients),
    path('private-recipes/<str:user_login>/', views.privateRecipes),
    path('filtered-recipes/<str:user_login>/', views.filteredRecipes),
    path('search-data/', views.searchBar),
]
