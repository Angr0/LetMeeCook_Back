import json

from django.forms import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from let_me_cook.models import AppUser, Recipe, Type, Ingredient, Category, Flavour, CookingHistory, StoredIngredient, \
    RecipeIngredient


# Create your views here.
@csrf_exempt
def manageUsers(request):
    if request.method == "POST":
        body = json.loads(request.body)
        dataObject = AppUser.objects.create(
            login=body['login'],
            password=body['password'],
            is_male=body['is_male'],
            height=body['height'],
            weight=body['weight'],
            age=body['age'],
            bmi=body['bmi'],
            bmr=body['bmr'],
            streak=0
        )
        dataObject.excluded_ingredients.add(None)
        dataObject.favourite_recipes.add(None)
        dataObject.save()
        return JsonResponse({"User added": {"login": dataObject.login}}, status=201)
    return noMethodPermission()


@csrf_exempt
def userData(request, user_login):
    if request.method == "GET":
        userObject = AppUser.objects.get(login=user_login)
        userDataset = {
            'login': userObject.login,
            'password': userObject.password,
            'is_male': userObject.is_male,
            'excluded_ingredients': list(userObject.excluded_ingredients.values_list('name', flat=True))
        }
        return JsonResponse(userDataset, status=302)
    if request.method == "PUT":
        body = json.loads(request.body)
        updatedUser = AppUser.objects.get(login=user_login)
        updatedUser.login = body['login']
        updatedUser.password = body['password']
        updatedUser.is_male = body['is_male']
        updatedUser.excluded_ingredients.clear()
        for ingredient in body['excluded_ingredients']:
            ingredientToExclude = Ingredient.objects.get(name=ingredient)
            updatedUser.excluded_ingredients.add(ingredientToExclude)
        updatedUser.save()
        return JsonResponse({"updated user": user_login}, status=302)
    return noMethodPermission()


@csrf_exempt
def userBmi(request, user_login):
    if request.method == "GET":
        userObject = AppUser.objects.get(login=user_login)
        bmiData = {
            'is_male': userObject.is_male,
            'height': userObject.height,
            'weight': userObject.weight,
            'age': userObject.age,
            'bmi': userObject.bmi,
            'bmr': userObject.bmr
        }
        return JsonResponse(bmiData, status=302)
    if request.method == "PUT":
        body = json.loads(request.body)
        updatedUser = AppUser.objects.get(login=user_login)
        updatedUser.age = body['age']
        updatedUser.bmi = body['bmi']
        updatedUser.bmr = body['bmr']
        updatedUser.height = body['height']
        updatedUser.weight = body['weight']
        updatedUser.save()
        return JsonResponse({"updated user": user_login}, status=302)
    return noMethodPermission()


@csrf_exempt
def fridge(request, user_login):
    if request.method == "GET":
        operatedUser = AppUser.objects.get(login=user_login)
        fridgeElements = StoredIngredient.objects.filter(appUser=operatedUser)
        storedList = []
        for ingredient in fridgeElements:
            ingredientDict = {
                'ingredient_name': ingredient.ingredient.name,
                'quantity': ingredient.quantity
            }
            storedList.append(ingredientDict)
        return JsonResponse(storedList, safe=False, status=302)
    if request.method == "PUT":
        ingredientsDicts = json.loads(request.body)
        operatedUser = AppUser.objects.get(login=user_login)
        for ingredientDict in ingredientsDicts:
            ingredientToAdd = Ingredient.objects.get(name=ingredientDict['name'])
            ingredientQuantity = ingredientDict['quantity']
            try:
                operatedStoredIngredient = StoredIngredient.objects.get(appUser=operatedUser, ingredient=ingredientToAdd)
                operatedStoredIngredient.quantity += ingredientQuantity
                operatedStoredIngredient.save()
            except StoredIngredient.DoesNotExist:
                addingStoredIngredient = StoredIngredient.objects.create(
                    appUser=operatedUser,
                    ingredient=ingredientToAdd,
                    quantity=ingredientQuantity
                )
                addingStoredIngredient.save()
        return JsonResponse({"Message": "Added ingredients and quantities to database"}, status=201)
    return noMethodPermission()


@csrf_exempt
def recipes(request):
    if request.method == "POST":
        body = json.loads(request.body)
        dataObject = Recipe.objects.create(
            name=body['name'],
            steps=body['steps'],
            is_warm=body['is_warm'],
            type=Type.objects.get(name=body['type_name']),
            icon_link=body['icon_link'],
            is_public=body['is_public'],
            author=AppUser.objects.get(login=body['user_login'])
        )
        dataObject.categories.add(*Category.objects.filter(name__in=body['categories']))
        dataObject.flavours.add(*Flavour.objects.filter(name__in=body['flavours']))
        dataObject.save()
        ingredientsDict = body['ingredients']
        for ingredientDict in ingredientsDict:
            ingredientToAdd = Ingredient.objects.get(name=ingredientDict['ingredient'])
            ingredientQuantity = ingredientDict['quantity']
            addingIngredient = RecipeIngredient.objects.create(
                ingredient=ingredientToAdd,
                recipe=dataObject,
                quantity=ingredientQuantity
            )
            addingIngredient.save()
        return JsonResponse({"Recipe added": {"name": dataObject.name}}, status=201)
    return noMethodPermission()


def recipe(request, recipe_name):
    if request.method == "GET":
        recipeToReturn = Recipe.objects.get(name=recipe_name)
        recipeIngredients = RecipeIngredient.objects.filter(recipe=recipeToReturn)
        ingredients = []
        for recipeIngredient in recipeIngredients:
            ingredientElement = {
                'ingredient': recipeIngredient.ingredient.name,
                'quantity': recipeIngredient.quantity,
                'unit': recipeIngredient.ingredient.unit_name
            }
            ingredients.append(ingredientElement)
        returnBody = {
            'name': recipeToReturn.name,
            'steps': recipeToReturn.steps,
            'ingredients': ingredients,
            'is_warm': recipeToReturn.is_warm,
            'icon_link': recipeToReturn.icon_link,
            'is_public': recipeToReturn.is_public,
            'categories': list(recipeToReturn.categories.values_list('name', flat=True)),
            'flavours': list(recipeToReturn.flavours.values_list('name', flat=True)),
            'type_name': recipeToReturn.type.name,
            'author_login': recipeToReturn.author.login
        }
        return JsonResponse(returnBody, status=302)
    return noMethodPermission()


@csrf_exempt
def cookingHistory(request, user_login=0):
    if request.method == "GET":
        userCook = AppUser.objects.get(login=user_login)
        meals = CookingHistory.objects.filter(user=userCook)
        mealsList = []
        for meal in meals:
            mealDict = {
                'name': meal.recipe.name,
                'portions': meal.portions,
                'date': meal.date
            }
            mealsList.append(mealDict)
        return JsonResponse(mealsList, safe=False, status=302)
    if request.method == "POST":
        body = json.loads(request.body)
        dataObject = CookingHistory.objects.create(
            user=AppUser.objects.get(login=body['user_login']),
            recipe=Recipe.objects.get(name=body['recipe_name']),
            portions=body['portions'],
            date=body['date']
        )
        dataObject.save()
        return JsonResponse({"History object added": {"user": dataObject.user.login, "recipe": dataObject.recipe.name}}, status=201)
    return noMethodPermission()


@csrf_exempt
def favouriteRecipes(request, user_login):
    if request.method == "GET":
        operatedUser = AppUser.objects.get(login=user_login)
        foundRecipes = operatedUser.favourite_recipes.all()
        returnRecipes = []
        for recipe in foundRecipes:
            recipeDict = {
                "name": recipe.name,
                "icon_link": recipe.icon_link,
                "type_name": recipe.type.name
            }
            returnRecipes.append(recipeDict)
        return JsonResponse(returnRecipes, safe=False, status=302)
    if request.method == "POST":
        operatedUser = AppUser.objects.get(login=user_login)
        body = json.loads(request.body)
        likedRecipe = Recipe.objects.get(name=body['name'])
        operatedUser.favourite_recipes.add(likedRecipe)
        operatedUser.save()
        return JsonResponse({"Added favourite recipe": likedRecipe.name}, status=201)
    if request.method == "DELETE":
        operatedUser = AppUser.objects.get(login=user_login)
        body = json.loads(request.body)
        recipeToRemove = Recipe.objects.get(name=body['name'])
        operatedUser.favourite_recipes.remove(recipeToRemove)
        operatedUser.save()
        return JsonResponse({"Removed favourite recipe": recipeToRemove.name}, status=202)
    return noMethodPermission()


def noMethodPermission():
    return JsonResponse({"error": "You have no permission for this method action"}, status=403)
