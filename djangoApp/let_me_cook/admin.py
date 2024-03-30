from django.contrib import admin

from let_me_cook.models import Ingredient, Category, Flavour, User, Recipe, CookingHistory

# Register your models here.
admin.site.register(Ingredient)
admin.site.register(Category)
admin.site.register(Flavour)
admin.site.register(User)
admin.site.register(Recipe)
admin.site.register(CookingHistory)
