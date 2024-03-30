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


class User(models.Model):
    login = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
    is_male = models.BooleanField()
    height = models.FloatField()
    weight = models.FloatField()
    age = models.PositiveIntegerField()
    bmi = models.FloatField()
    bmr = models.FloatField()
    streak = models.PositiveIntegerField()
    excluded_ingredients = models.ManyToManyField(Ingredient, related_name='user_excluded_ingredient')
    favourite_recipes = models.ManyToManyField('Recipe')
    stored_ingredients = models.ManyToManyField(Ingredient, related_name='user_stored_ingredient')

    def __str__(self):
        return f"{self.login}"


class Recipe(models.Model):
    name = models.CharField(max_length=250)
    ingredients = models.ManyToManyField(Ingredient)
    steps = models.CharField(max_length=10000)
    is_warm = models.BooleanField()
    type = models.CharField(max_length=250)
    categories = models.ManyToManyField(Category)
    flavours = models.ManyToManyField(Flavour)
    icon_link = models.CharField(max_length=10000)
    is_public = models.BooleanField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"


class CookingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    recipe = models.ForeignKey(Recipe, on_delete=models.DO_NOTHING)
    portions = models.PositiveIntegerField()
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.login}; {self.recipe.name}"
