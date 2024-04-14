from django.contrib import admin

from let_me_cook.models import Ingredient, Category, Flavour, AppUser, Recipe, CookingHistory, Type, StoredIngredient, \
    RecipeIngredient, Step, ShoppingList

# Register your models here.
admin.site.register(Ingredient)
admin.site.register(Category)
admin.site.register(Flavour)
admin.site.register(AppUser)
admin.site.register(Recipe)
admin.site.register(CookingHistory)
admin.site.register(Type)
admin.site.register(StoredIngredient)
admin.site.register(RecipeIngredient)
admin.site.register(Step)
admin.site.register(ShoppingList)
