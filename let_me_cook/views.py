import json
import hashlib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from let_me_cook.models import AppUser, Recipe, Type, Ingredient, Category, Flavour, CookingHistory, StoredIngredient, \
    RecipeIngredient, Step, ShoppingList


# Create your views here.
@csrf_exempt
def manageUsers(request):
    if request.method == "POST":
        body = json.loads(request.body)
        dataObject = AppUser.objects.create(
            login=body['login'],
            password=hashlib.sha256(body['password'].encode('utf-8')).hexdigest(),
            is_male=body['is_male'],
            height=body['height'],
            weight=body['weight'],
            age=body['age'],
            streak=0
        )
        dataObject.excluded_ingredients.add(None)
        dataObject.favourite_recipes.add(None)
        dataObject.save()
        return JsonResponse({"User added": {"login": dataObject.login}}, status=201)
    return noMethodPermission()


@csrf_exempt
def loginUser(request):
    if request.method == "POST":
        loginData = json.loads(request.body)
        try:
            tryUser = AppUser.objects.get(login=loginData['login'])
            tryPassword = hashlib.sha256(loginData['password'].encode('utf-8')).hexdigest()
            if tryPassword == tryUser.password:
                return JsonResponse({"password matches": True}, status=200)
            else:
                return JsonResponse({"password matches": False}, status=403)
        except AppUser.DoesNotExist:
            return JsonResponse({"error": "user does not exist"}, status=403)
    return noMethodPermission()


@csrf_exempt
def userData(request, user_login):
    if request.method == "GET":
        userObject = AppUser.objects.get(login=user_login)
        userDataset = {
            'login': userObject.login,
            'is_male': userObject.is_male,
            'excluded_ingredients': list(userObject.excluded_ingredients.values('name', 'icon_link'))
        }
        return JsonResponse(userDataset, status=200)
    if request.method == "PUT":
        body = json.loads(request.body)
        updatedUser = AppUser.objects.get(login=user_login)
        ingredientToExclude = Ingredient.objects.get(name=body['name'])
        updatedUser.excluded_ingredients.add(ingredientToExclude)
        updatedUser.save()
        return JsonResponse({"updated user": user_login}, status=200)
    if request.method == "DELETE":
        body = json.loads(request.body)
        updatedUser = AppUser.objects.get(login=user_login)
        ingredientToInclude = Ingredient.objects.get(name=body['name'])
        updatedUser.excluded_ingredients.remove(ingredientToInclude)
        updatedUser.save()
        return JsonResponse({"updated user": user_login}, status=200)
    return noMethodPermission()


@csrf_exempt
def changePassword(request, user_login):
    if request.method == "PUT":
        body = json.loads(request.body)
        updatedUser = AppUser.objects.get(login=user_login)
        newPass = hashlib.sha256(body['password'].encode('utf-8')).hexdigest()
        updatedUser.password = newPass
        updatedUser.save()
        return JsonResponse({"changed password for user": updatedUser.login})
    return noMethodPermission()


@csrf_exempt
def clearFridge(request, user_login):
    if request.method == "DELETE":
        operatedUser = AppUser.objects.get(login=user_login)
        StoredIngredient.objects.filter(appUser=operatedUser).delete()
        return JsonResponse({"cleared fridge of user": operatedUser.login}, status=200)
    return noMethodPermission()


def allIngredients(request):
    if request.method == "GET":
        allIngredients = Ingredient.objects.values('name', 'unit_name', 'icon_link')
        return JsonResponse(list(allIngredients), safe=False, status=200)
    return noMethodPermission()


def notExcludedIngredients(request, user_login):
    if request.method == "GET":
        updatedUser = AppUser.objects.get(login=user_login)
        excludedIngredients = list(updatedUser.excluded_ingredients.values_list('name', flat=True))
        noExcludedIngredients = list(Ingredient.objects.exclude(name__in=excludedIngredients).values('name', 'icon_link'))
        return JsonResponse(noExcludedIngredients, safe=False, status=200)
    return noMethodPermission()


@csrf_exempt
def ingredients(request):
    if request.method == "POST":
        ingredientsList = json.loads(request.body)
        foundIngredients = Ingredient.objects.filter(name__in=ingredientsList)
        ingredientsToReturn = []
        for ingredient in foundIngredients:
            ingredientObject = {
                'name': ingredient.name,
                'unit_name': ingredient.unit_name,
                'icon_link': ingredient.icon_link
            }
            ingredientsToReturn.append(ingredientObject)
        return JsonResponse(ingredientsToReturn, safe=False, status=200)
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
        }
        return JsonResponse(bmiData, status=200)
    if request.method == "PUT":
        body = json.loads(request.body)
        updatedUser = AppUser.objects.get(login=user_login)
        updatedUser.age = body['age']
        updatedUser.height = body['height']
        updatedUser.weight = body['weight']
        updatedUser.save()
        return JsonResponse({"updated user": user_login}, status=200)
    return noMethodPermission()


def returnRecipes(foundRecipes):
    recipesToReturn = []
    for foundRecipe in foundRecipes:
        recipeIngredients = RecipeIngredient.objects.filter(recipe=foundRecipe)
        ingredientsList = []
        for recipeIngredient in recipeIngredients:
            ingredientsList.append(recipeIngredient.ingredient.name)
        recipeObject = {
            'name': foundRecipe.name,
            'icon_link': foundRecipe.icon_link,
            'is_warm': foundRecipe.is_warm,
            'flavours': list(foundRecipe.flavours.values_list('name', flat=True)),
            'type': foundRecipe.type.name,
            'categories': list(foundRecipe.categories.values_list('name', flat=True)),
            'ingredients': ingredientsList
        }
        recipesToReturn.append(recipeObject)
    return JsonResponse(recipesToReturn, safe=False, status=200)


@csrf_exempt
def fridge(request, user_login):
    if request.method == "GET":
        operatedUser = AppUser.objects.get(login=user_login)
        fridgeElements = StoredIngredient.objects.filter(appUser=operatedUser)
        storedList = []
        for ingredient in fridgeElements:
            ingredientDict = {
                'ingredient_name': ingredient.ingredient.name,
                'quantity': ingredient.quantity,
                'unit_name': ingredient.ingredient.unit_name,
                'icon_link': ingredient.ingredient.icon_link
            }
            storedList.append(ingredientDict)
        return JsonResponse(storedList, safe=False, status=200)
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
        return JsonResponse({"Message": "Added ingredients and quantities to database"}, status=200)
    if request.method == "DELETE":
        operatedUser = AppUser.objects.get(login=user_login)
        ingredientToDeleteName = json.loads(request.body)
        for ingredientElement in ingredientToDeleteName:
            ingredientObject = Ingredient.objects.get(name=ingredientElement)
            ingredientToDelete = StoredIngredient.objects.get(appUser=operatedUser, ingredient=ingredientObject)
            ingredientToDelete.delete()
            return JsonResponse({"Deleted ingredient from fridge": ingredientElement}, status=200)
    return noMethodPermission()


def checkFridgeQuantity(operatedUser, recipesList):
    fridgeAccurateRecipes = []
    for recipeElement in recipesList:
        allRecipeIngredients = list(RecipeIngredient.objects.filter(recipe=recipeElement))
        canAdd = True
        for recipeIngredient in allRecipeIngredients:
            print(recipeIngredient)
            requiredIngredientQuantity = recipeIngredient.quantity
            try:
                fridgeUserIngredient = StoredIngredient.objects.get(appUser=operatedUser, ingredient=recipeIngredient.ingredient)
                fridgeIngredientQuantity = fridgeUserIngredient.quantity
            except StoredIngredient.DoesNotExist:
                fridgeIngredientQuantity = 0
            if fridgeIngredientQuantity < requiredIngredientQuantity:
                canAdd = False
                break
        if canAdd:
            fridgeAccurateRecipes.append(recipeElement)
    return fridgeAccurateRecipes


def filteredRecipes(request, user_login):
    if request.method == "GET":
        operatedUser = AppUser.objects.get(login=user_login)
        excludedIngredientsList = list(operatedUser.excluded_ingredients.all())
        recipesWithoutExcluded = Recipe.objects.exclude(ingredients__in=excludedIngredientsList)
        fridgeFilteredRecipes = checkFridgeQuantity(operatedUser, recipesWithoutExcluded)
        return returnRecipes(fridgeFilteredRecipes)
    return noMethodPermission()


@csrf_exempt
def recipes(request):
    if request.method == "GET":
        recipesToReturn = Recipe.objects.filter(is_public=True)
        return returnRecipes(recipesToReturn)
    if request.method == "POST":
        body = json.loads(request.body)
        dataObject = Recipe.objects.create(
            name=body['name'],
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
        stepsList = body['steps']
        for step in stepsList:
            stepObject = Step.objects.create(
                recipe=dataObject,
                step_number=step['number'],
                step_description=step['description']
            )
            stepObject.save()
        return JsonResponse({"Recipe added": {"name": dataObject.name}}, status=200)
    return noMethodPermission()


def privateRecipes(request, user_login):
    if request.method == "GET":
        operatedUser = AppUser.objects.get(login=user_login)
        userRecipes = Recipe.objects.filter(is_public=False, author=operatedUser)
        return returnRecipes(userRecipes)
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
        recipeSteps = Step.objects.filter(recipe=recipeToReturn)
        steps = []
        for recipeStep in recipeSteps:
            stepElement = {
                'number': recipeStep.step_number,
                'description': recipeStep.step_description
            }
            steps.append(stepElement)
        returnBody = {
            'name': recipeToReturn.name,
            'ingredients': ingredients,
            'is_warm': recipeToReturn.is_warm,
            'icon_link': recipeToReturn.icon_link,
            'categories': list(recipeToReturn.categories.values_list('name', flat=True)),
            'flavours': list(recipeToReturn.flavours.values_list('name', flat=True)),
            'type_name': recipeToReturn.type.name,
            'author_login': recipeToReturn.author.login,
            'steps': steps
        }
        return JsonResponse(returnBody, status=200)
    return noMethodPermission()


def searchBar(request):
    if request.method == "GET":
        allRecipes = Recipe.objects.all()
        returnData = []
        for operatedRecipe in allRecipes:
            recipeIngredients = RecipeIngredient.objects.filter(recipe=operatedRecipe)
            ingredients = []
            for recipeIngredient in recipeIngredients:
                ingredients.append(recipeIngredient.ingredient.name)
            recipeObject = {
                'name': operatedRecipe.name,
                'icon_link': operatedRecipe.icon_link,
                'ingredients': ingredients
            }
            returnData.append(recipeObject)
        return JsonResponse(returnData, safe=False, status=200)
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
                'date': meal.date,
                'icon_link': meal.recipe.icon_link
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
        return JsonResponse({"History object added": {"user": dataObject.user.login, "recipe": dataObject.recipe.name}}, status=200)
    return noMethodPermission()


@csrf_exempt
def favouriteRecipes(request, user_login):
    if request.method == "GET":
        operatedUser = AppUser.objects.get(login=user_login)
        foundRecipes = operatedUser.favourite_recipes.all()
        return returnRecipes(foundRecipes)
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
        return JsonResponse({"Removed favourite recipe": recipeToRemove.name}, status=200)
    return noMethodPermission()


def categories(request):
    if request.method == "GET":
        allCategories = Category.objects.values_list('name', flat=True)
        return JsonResponse(list(allCategories), safe=False, status=200)
    return noMethodPermission()


def flavours(request):
    if request.method == "GET":
        allFlavours = Flavour.objects.values_list('name', flat=True)
        return JsonResponse(list(allFlavours), safe=False, status=200)
    return noMethodPermission()


@csrf_exempt
def shoppingList(request, user_login):
    if request.method == "PUT":
        operatedUser = AppUser.objects.get(login=user_login)
        ingredientsDicts = json.loads(request.body)
        for ingredientDict in ingredientsDicts:
            ingredientToAdd = Ingredient.objects.get(name=ingredientDict['name'])
            ingredientQuantity = ingredientDict['quantity']
            try:
                operatedShoppingIngredient = ShoppingList.objects.get(appUser=operatedUser, ingredient=ingredientToAdd)
                operatedShoppingIngredient.quantity += ingredientQuantity
                operatedShoppingIngredient.save()
            except ShoppingList.DoesNotExist:
                addingShoppingIngredient = ShoppingList.objects.create(
                    appUser=operatedUser,
                    ingredient=ingredientToAdd,
                    quantity=ingredientQuantity
                )
                addingShoppingIngredient.save()
        return JsonResponse({"Message": "Added ingredients to shopping list"}, status=200)
    if request.method == "DELETE":
        operatedUser = AppUser.objects.get(login=user_login)
        ingredientsToAdd = ShoppingList.objects.filter(appUser=operatedUser)
        for shoppingIngredient in ingredientsToAdd:
            try:
                alreadyStoredIngredient = StoredIngredient.objects.get(appUser=operatedUser, ingredient=shoppingIngredient.ingredient)
                alreadyStoredIngredient.quantity += shoppingIngredient.quantity
                alreadyStoredIngredient.save()
            except StoredIngredient.DoesNotExist:
                addingStoredIngredient = StoredIngredient.objects.create(
                    appUser=operatedUser,
                    ingredient=shoppingIngredient.ingredient,
                    quantity=shoppingIngredient.quantity
                )
                addingStoredIngredient.save()
        ShoppingList.objects.filter(appUser=operatedUser).delete()
        return JsonResponse({"completed shopping list of user": operatedUser.login}, status=200)
    return noMethodPermission()


def noMethodPermission():
    return JsonResponse({"error": "You have no permission for this method action"}, status=403)
