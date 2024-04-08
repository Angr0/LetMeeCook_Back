from django.db import models


# Create your models here.
class Ingredient(models.Model):
    name = models.CharField(max_length=250)
    unit_name = models.CharField(max_length=250)
    icon_link = models.CharField(max_length=10000)

    def __str__(self):
        return f"{self.name}"


class Category(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.name}"


class Flavour(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.name}"


class Type(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.name}"


class AppUser(models.Model):
    login = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
    is_male = models.BooleanField()
    height = models.FloatField()
    weight = models.FloatField()
    age = models.PositiveIntegerField()
    bmi = models.FloatField()
    bmr = models.FloatField()
    streak = models.PositiveIntegerField()
    excluded_ingredients = models.ManyToManyField(Ingredient, related_name='user_excluded_ingredient', blank=True)
    favourite_recipes = models.ManyToManyField('Recipe', blank=True)
    stored_ingredients = models.ManyToManyField(Ingredient, blank=True, through='StoredIngredient')

    def __str__(self):
        return f"{self.login}"


class StoredIngredient(models.Model):
    appUser = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()


class Recipe(models.Model):
    name = models.CharField(max_length=250)
    ingredients = models.ManyToManyField(Ingredient, blank=True, through='RecipeIngredient')
    steps = models.CharField(max_length=10000)
    is_warm = models.BooleanField()
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)
    flavours = models.ManyToManyField(Flavour)
    icon_link = models.CharField(max_length=10000)
    is_public = models.BooleanField()
    author = models.ForeignKey(AppUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.FloatField()


class CookingHistory(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.DO_NOTHING)
    recipe = models.ForeignKey(Recipe, on_delete=models.DO_NOTHING)
    portions = models.PositiveIntegerField()
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.login}; {self.recipe.name}"
