from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize

from core.models import *
from django.http import JsonResponse, HttpResponseRedirect
import json
import random
from datetime import datetime


def finish_task(index, username):
    user = CustomUser.objects.get(username=username)
    character = user.character

    # start daily dungeon raid and level up/ gain exp
    messageBoard = ''
    user.target_num_quests_inc = user.target_num_quests_inc + 1
    if user.target_num_quests_inc == user.target_num_quests:
        character.exp = character.exp + 25
        if character.exp == 100:
            character.exp = 0
            character.level = character.level + 1
            if character.can_advance_rank():
                if character.advance_rank():
                    messageBoard = "Nice Job! You ranked up!"
            else:
                pass
            messageBoard = "You've leveled up! This is proof that your hard work and perseverance are paying off. Keep pushing forward—greater challenges bring even greater rewards!"
            character.save()
            user.save()
        character.save()
    # ^^^^
    # below is getting the percentage for the progression overview
    Quest = dailyQuest.objects.get(quest_name=index)
    user.completed_quests = user.completed_quests + 1
    user.percent_weekly_completed = round((user.completed_quests / user.weekly_quests_count) * 100)
    if user.percent_weekly_completed >= 100.00:
        # print("Week compelte")
        messageBoard = "You've conquered the week like a true hero—each day a step closer to your goals. Take pride in your progress and remember, every small victory fuels the next great adventure!"
        user.percent_weekly_completed = 0.00
        user.save()
    user.save()
    number_of_quests = user.number_of_quests
    new_number_of_quests = number_of_quests - 1
    drops = Quest.get_drops()
    # get updated char.exp
    charExp = character.exp

    # drops
    for item_id in drops:
        item = Item.objects.get(id=item_id)

        backpack_item, created = BackpackItem.objects.get_or_create(
            character=character,
            item=item,
        )
        if not created:
            backpack_item.quantity += 1
            backpack_item.save()

    if messageBoard == '':
        return {'NumberQuest': new_number_of_quests, 'drops': drops, 'charExp': charExp}
    else:
        return {'NumberQuest': new_number_of_quests, 'drops': drops, 'charExp': charExp, "messageBoard": messageBoard}


def get_random_quests(num_quests, username):
    user = CustomUser.objects.get(username=username)
    character = user.character
    Quest = dailyQuest.objects.all()
    dQuest = list(Quest)
    random_quests = random.sample(dQuest, num_quests)
    character.quests.add(*random_quests)
    character.save()
    return random_quests


def named_drops(drop):
    items = Item.objects.filter(id__in=drop)
    id_to_name = {item.id: item.name for item in items}
    names = [id_to_name.get(item_id, "Unknown") for item_id in drop]
    return names


def addItemToBag(itemToAdd, username):
    user = CustomUser.objects.get(username=username)
    character = user.character
    if isinstance(itemToAdd, int):
        item = Item.objects.get(id=itemToAdd)
    elif isinstance(itemToAdd, str):
        item = Item.objects.get(name=itemToAdd)
    if item.marketable:
        itemPrice = item.price
        if character.gold >= itemPrice:
            character.gold = character.gold - itemPrice
            character.save()
        else:
            return 2

    backpack_item, created = BackpackItem.objects.get_or_create(
        character=character,
        item=item,
    )
    if not created:
        backpack_item.quantity += 1
        backpack_item.save()
    return 1


def check_efficiency(efficiency, weapon_bag):
    if 4.0 <= efficiency < 5.0:
        weapon_bag.upgraded_damage = weapon_bag.upgraded_damage + 1
    elif efficiency == 10.0:
        weapon_bag.upgraded_damage = weapon_bag.upgraded_damage + 2
    weapon_bag.save()


def check_Magic_Efficiency(efficiency, magicTome, magic):
    if 4.0 <= efficiency < 5.0:
        if magic.damage != 0:
            magicTome.damage_modifier = magicTome.damage_modifier + 1
        elif magic.healing != 0:
            magicTome.healing_modifier = magicTome.healing_modifier + 1
    elif efficiency == 10.0:
        magicTome.upgraded_damage = magicTome.upgraded_damage + 2
    magicTome.save()


def addWeapon(itemName, character):
    weaponToAdd = Weapon.objects.get(name=itemName)
    backpack = BackpackItem.objects.filter(character_id=character.id, item__forgeIngredient=True, )
    # print(weaponToAdd)
    ingredientsList = [
        {"name": ingredient.item.name,
         "quantity": ingredient.quantity,
         "id": ingredient.item.id
         }
        for ingredient in equipablesIngredients.objects.filter(weapon=weaponToAdd.id)
    ]
    backpack_data = [
        {
            "id": item.item_id,
            "name": item.item.name,
            "quantity": item.quantity,
        }
        for item in backpack
    ]
    # print(backpack_data)
    all_items_good = True
    for ingredient in ingredientsList:
        matching_item = next(
            (item for item in backpack_data if
             item["name"] == ingredient["name"] and item["quantity"] >= ingredient["quantity"]),
            None
        )
        if not matching_item:
            all_items_good = False
            message = f"Missing or insufficient quantity for: {ingredient['name']}"
            return JsonResponse({'message': message}, status=200)

    for ingredient in ingredientsList:
        queried_item = BackpackItem.objects.get(item=ingredient['id'], character_id=character.id)
        queried_item.quantity = queried_item.quantity - ingredient['quantity']
        queried_item.save()
    character.weapons.add(weaponToAdd)
    weaponBag = WeaponBag.objects.filter(character=character.id, weapon=weaponToAdd.id).first()
    weaponBag.current_durability = weaponToAdd.max_durability
    weaponBag.save()
    return JsonResponse({'message': 'Completed', 'ingredients': ingredientsList}, status=200)


def addArmor(itemName, character):
    armorToAdd = Armor.objects.get(name=itemName)
    backpack = BackpackItem.objects.filter(character_id=character.id, item__forgeIngredient=True, )
    # print(weaponToAdd)
    ingredientsList = [
        {"name": ingredient.item.name,
         "quantity": ingredient.quantity,
         "id": ingredient.item.id
         }
        for ingredient in equipablesIngredients.objects.filter(armor=armorToAdd.id)
    ]
    # print(ingredientsList)
    backpack_data = [
        {
            "id": item.item_id,
            "name": item.item.name,
            "quantity": item.quantity,
        }
        for item in backpack
    ]
    # print(backpack_data)
    all_items_good = True
    for ingredient in ingredientsList:
        # print(ingredient)
        matching_item = next(
            (item for item in backpack_data if
             item["name"] == ingredient["name"] and item["quantity"] >= ingredient["quantity"]),
            None
        )
        if not matching_item:
            all_items_good = False
            message = f"Missing or insufficient quantity for: {ingredient['name']}"
            return JsonResponse({'message': message}, status=200)

    for ingredient in ingredientsList:
        queried_item = BackpackItem.objects.get(item=ingredient['id'], character_id=character.id)
        queried_item.quantity = queried_item.quantity - ingredient['quantity']
        queried_item.save()
    character.armor.add(armorToAdd)
    armorBag = ArmorBag.objects.filter(character=character.id, armor=armorToAdd.id).first()
    armorBag.current_durability = armorToAdd.max_durability
    armorBag.save()
    return JsonResponse({'message': 'Completed', "ingredients": ingredientsList}, status=200)


def addSkill(skill, character):
    skillset = skillSet.objects.filter(character_id=character.id, skill_id=skill.id).first()
    if skillset:
        if skillset.efficiency < 10:
            skillset.efficiency = skillset.efficiency + 1
            if skill.damage != 0:
                skillset.damage_modifier = skillset.damage_modifier + 1
            elif skill.healing != 0:
                skillset.healing_modifier = skillset.healing_modifier + 1
            skillset.save()
            return {"message": "LevelUp", "damage": skillset.damage_modifier, "efficiency": skillset.efficiency}
        else:
            return "Max Efficiency"
    else:
        character.skills.add(skill)
        character.save()
        skillset = skillSet.objects.get(character_id=character.id, skill_id=skill.id)
        if skill.damage != 0:
            skillset.damage_modifier = skill.damage
        elif skill.healing != 0:
            skillset.healing_modifier = skill.healing
        skillset.efficiency = skillset.efficiency + 1
        skillset.save()
        return {"message": "LevelUp", "efficiency": skillset.efficiency}


def practiceWeapon(weapon, weapon_bag, character, type):
    if type == 'safe':
        if weapon_bag.weapon_efficiency <= 5:
            num = random.randint(1, 100)
            if num >= 50:
                character.current_motivation = character.current_motivation - 1
                character.current_health = character.current_health - 1
                weapon_bag.weapon_efficiency = weapon_bag.weapon_efficiency + 0.25
                check_efficiency(weapon_bag.weapon_efficiency, weapon_bag)
                character.save()
                weapon_bag.save()
                return 1  # Damage
            else:
                character.current_motivation = character.current_motivation - 1
                weapon_bag.weapon_efficiency = weapon_bag.weapon_efficiency + 0.50
                check_efficiency(weapon_bag.weapon_efficiency, weapon_bag)
                character.save()
                weapon_bag.save()
                return 2  # good

        else:
            weapon_bag.weapon_efficiency = weapon_bag.weapon_efficiency + 0.50
            character.current_motivation = character.current_motivation - 1
            check_efficiency(weapon_bag.weapon_efficiency, weapon_bag)
            character.save()
            weapon_bag.save()
            return 2  # good
    elif type == 'intense':
        if weapon_bag.weapon_efficiency <= 5:
            num = random.randint(1, 100)
            if num >= 30:
                character.current_motivation = character.current_motivation - 1
                character.current_health = character.current_health - 2
                character.save()
                weapon_bag.save()
                return 1  # Damage
            else:
                character.current_motivation = character.current_motivation - 1
                weapon_bag.weapon_efficiency = weapon_bag.weapon_efficiency + 1
                check_efficiency(weapon_bag.weapon_efficiency, weapon_bag)
                character.save()
                weapon_bag.save()
                return 3  # amazing
        else:
            weapon_bag.weapon_efficiency = weapon_bag.weapon_efficiency + 1
            character.current_motivation = character.current_motivation - 1
            check_efficiency(weapon_bag.weapon_efficiency, weapon_bag)

            character.save()
            weapon_bag.save()
            return 3  # amazing


def practiceMagic(magic, magic_tome, character, type):
    if type == 'safe':
        if magic_tome.spell_efficiency <= 5:
            num = random.randint(1, 100)
            if num >= 50:
                character.current_motivation = character.current_motivation - 1
                character.current_health = character.current_health - 1
                magic_tome.spell_efficiency = magic_tome.spell_efficiency + 0.25
                check_Magic_Efficiency(magic_tome.spell_efficiency, magic_tome, magic)
                character.save()
                magic_tome.save()
                return 1  # Damage
            else:
                character.current_motivation = character.current_motivation - 1
                magic_tome.spell_efficiency = magic_tome.spell_efficiency + 0.50
                check_Magic_Efficiency(magic_tome.spell_efficiency, magic_tome, magic)
                character.save()
                magic_tome.save()
                return 2  # good

        else:
            magic_tome.spell_efficiency = magic_tome.spell_efficiency + 0.50
            character.current_motivation = character.current_motivation - 1
            check_Magic_Efficiency(magic_tome.spell_efficiency, magic_tome, magic)
            character.save()
            magic_tome.save()
            return 2  # good
    elif type == 'intense':
        if magic_tome.spell_efficiency <= 5:
            num = random.randint(1, 100)
            if num >= 30:
                character.current_motivation = character.current_motivation - 1
                character.current_health = character.current_health - 2
                character.save()
                return 1  # Damage
            else:
                character.current_motivation = character.current_motivation - 1
                magic_tome.spell_efficiency = magic_tome.spell_efficiency + 1
                check_Magic_Efficiency(magic_tome.spell_efficiency, magic_tome, magic)
                character.save()
                magic_tome.save()
                return 3  # amazing
        else:
            magic_tome.spell_efficiency = magic_tome.spell_efficiency + 1
            character.current_motivation = character.current_motivation - 1
            check_Magic_Efficiency(magic_tome.spell_efficiency, magic_tome, magic)
            character.save()
            magic_tome.save()
            return 3  # amazing


# routes

def homePage(request):
    return render(request, template_name="home.html")


def loginPage(request):
    if request.method == "POST":
        form = loginForm(data=request.POST or None)
        RegForm = CustomUserCreationForm(data=request.POST or None)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard', username=username)
        if RegForm.is_valid():
            RegForm.save()
            username = RegForm.cleaned_data['username']
            password = RegForm.cleaned_data['password1']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                rank = Rank.objects.get(name="Weak")
                user1 = CustomUser.objects.get(username=username)
                new_character = Character.objects.create(character_name=username)
                character = Character.objects.get(character_name=username)
                character.rank = rank
                user1.character = new_character
                user1.save()
                character.save()
                return redirect('dashboard', username=username)
        else:
            print(RegForm.errors)
            return redirect('home')
    else:
        form = loginForm()
        RegForm = CustomUserCreationForm()
    return render(request, "login.html", {'form': form, 'reg': RegForm, 'errors': RegForm.errors})


@login_required
def logoutPage(request):
    logout(request)
    return redirect('home')


@login_required
def dashboardPage(requests, username):
    user = CustomUser.objects.get(username=username)
    character = user.character
    if user.base_number_of_quests > 0:
        user.weekly_quests_count = user.base_number_of_quests * 7
        user.save()
    backpack_items = BackpackItem.objects.filter(character=character)
    last_four_items = backpack_items.order_by('-id')[:1]
    number_of_quests = user.number_of_quests
    if requests.method == "POST":
        data = json.loads(requests.body.decode('utf-8'))
        message = data.get('message')
        if message == 'Finish task!':  # takes the looped Json from finished_task_route
            NumberQuests = data.get('NumberQuest')
            questID = data.get('questID')
            # print(f"change_noq is {NumberQuests}")
            user.number_of_quests = NumberQuests
            quest_to_remove = character.quests.filter(id=questID)
            character.quests.remove(*quest_to_remove)
            user.save()
            character.save()
            new_num_quests = user.number_of_quests
            return JsonResponse(
                {"message": "Task completed successfully from dashboard!", "newNumQuest": new_num_quests}, status=200)
        elif message == 'Get quest details!':  # gets quest details from frontend
            data = json.loads(requests.body.decode('utf-8'))
            quests = data.get('quests')
            fetchedQuest = dailyQuest.objects.filter(quest_name__in=quests)
            questDescription = {}
            for i in fetchedQuest:
                questDescription[i.quest_name] = i.quest_description
            return JsonResponse(
                {"message": "Task completed successfully from quest details!", 'questDescription': questDescription},
                status=200)
    if requests.method == "GET":
        if number_of_quests == 0:
            user.gotten_quests = False
            if character.current_motivation > 0:
                calcMotivation = (character.current_motivation / character.motivation * 100)
            if character.current_health > 0:
                calcHealth = (character.current_health / character.health * 100)
            return render(requests, "dashboard.html", {'user': user, "items": last_four_items, "character": character,
                                                       "calcMotivation": calcMotivation, "calcHealth": calcHealth})
        else:
            if user.gotten_quests:
                dquest = character.quests.all()
                # print(character.current_motivation)
                if character.current_motivation > 0:
                    calcMotivation = (character.current_motivation / character.motivation * 100)
                else:
                    calcMotivation = 0
                if character.current_health > 0:
                    calcHealth = (character.current_health / character.health * 100)
                    # print(calcHealth)
                else:
                    calcHealth = 0
                return render(requests, "dashboard.html",
                              {'user': user, 'dQuest': dquest, "NumQuest": number_of_quests, "items": last_four_items,
                               "character": character, "calcMotivation": calcMotivation, "calcHealth": calcHealth})
            else:
                character.quests.clear()
                user.gotten_quests = True
                user.save()
                dquest = get_random_quests(number_of_quests, username)
                if character.current_motivation > 0:
                    calcMotivation = (character.motivation / character.current_motivation)
                if character.current_health > 0:
                    calcHealth = (character.health / character.current_health)
                    # print(calcHealth)
                return render(requests, "dashboard.html", {'user': user, 'dQuest': dquest, "NumQuest": number_of_quests,
                                                           "items": last_four_items, "character": character,
                                                           "calcMotivation": calcMotivation,
                                                           "calcHealth": calcHealth})


@login_required
def finish_task_route(request, username):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        task_index = data.get('taskIndex')

        task_complete = finish_task(task_index, username)  # sends to function

        # desturctue the task_complete
        NumberQuest = task_complete.get('NumberQuest')
        charExp = task_complete.get('charExp')
        drops = task_complete.get('drops')
        questName = data.get('questName')
        messageB = data.get('messageBoard')
        if messageB is None:
            messageB = f'You completed "{questName}", congratulations!'
        else:
            pass
        # process drops
        named_drop = named_drops(drops)
        # db query
        completedQuest = dailyQuest.objects.get(quest_name=questName)
        user = CustomUser.objects.get(username=username)
        # send out from queries
        completed = user.percent_weekly_completed
        questID = completedQuest.id

        send_out = {"message": "Finish task!",
                    "NumberQuest": NumberQuest,
                    "drops": named_drop,
                    "completed": completed,
                    "charExp": charExp,
                    "questID": questID,
                    "messageBoard": messageB
                    }
        return JsonResponse(send_out, status=200)


@login_required
def characterPage(request, username):
    user = CustomUser.objects.get(username=username)
    character = user.character
    return render(request, "character.html", {'character': character, 'user': user})


@login_required
def worldMapPage(request, username):
    return render(request, "worldMap.html")


@login_required
def marketView(request, username):
    user = CustomUser.objects.get(username=username)
    character = user.character
    return render(request, "market.html", {'user': user, "character": character})


@login_required
def marketViewSendItems(request, username):
    items = Item.objects.filter(marketable=True)
    if request.method == "GET":
        itemsToPage = []
        randomized_items = items.order_by('?')
        for item in randomized_items:
            if random.uniform(0, 100) <= item.market_drop_rate:
                itemsToPage.append({
                    'item': item.name,
                    'price': item.price,
                    'description': item.description,
                    'type': item.type

                })
        return JsonResponse(itemsToPage, status=200, safe=False, )

    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        user = data.get('username')
        item = data.get('itemName')
        result = addItemToBag(item, user)
        if result == 1:
            send_out = {"message": "Task completed successfully!", "item": item}
            return JsonResponse(send_out, status=200)
        else:
            send_out = {"message": "Insufficient funds", "item": item}
            return JsonResponse(send_out, status=200)


@login_required
def blackSmithView(request, username):
    user = CustomUser.objects.get(username=username)
    character = user.character
    return render(request, "blackSmith.html", {'user': user, "character": character})


@login_required
def blackSmithFetch(request, username):
    if request.method == "GET":
        message = request.headers.get('X-Custom-Message')
        userName = request.headers.get('X-Custom-User')
        user = CustomUser.objects.get(username=userName)
        character = user.character
        backpack = BackpackItem.objects.filter(
            character_id=character.id,
            item__forgeIngredient=True,
        )
        backpack_data = [
            {
                "id": item.item_id,
                "name": item.item.name,
                "quantity": item.quantity,
            }
            for item in backpack
        ]

        if message == "smelt":
            filtered_backpack_data = [
                item for item in backpack_data if "ore" in item["name"].lower()
            ]
            if not filtered_backpack_data:
                return JsonResponse({'message': 'Completed'}, status=200)
            else:
                return JsonResponse({'message': 'Completed', 'backpack': filtered_backpack_data}, status=200)
        elif message == "forge":
            forgeables = []
            weapons = Weapon.objects.filter(forgeable=True)
            armors = Armor.objects.filter(forgeable=True)
            for item in list(weapons) + list(armors):
                item_type = 'weapon' if isinstance(item, Weapon) else 'armor'
                forgeables.append({
                    "name": item.name,
                    "id": item.id,
                    "type": item_type,
                    "ingredients": [
                        {"name": ingredient.item.name, "quantity": ingredient.quantity}
                        for ingredient in equipablesIngredients.objects.filter(
                            **{item_type: item}
                        )
                    ]
                })

            items = [
                {"id": item.item_id,
                 "name": item.item.name,
                 "quantity": item.quantity}
                for item in backpack
                if hasattr(item.item, "forgeIngredient")
            ]
            if not items:
                return JsonResponse({'message': 'Forge', "forgeables": forgeables}, status=200)
            else:
                return JsonResponse({'message': 'Forge', "items": items, "forgeables": forgeables}, status=200)
        elif message == "repair":
            items = list(character.weapons.all()) + list(character.armor.all())

            item_data = []

            for item in items:
                if isinstance(item, Weapon):
                    Cquantity = WeaponBag.objects.filter(character=character.id, weapon=item.id).first()
                    current_durability = Cquantity.current_durability
                    item_type = "weapon"
                elif isinstance(item, Armor):
                    Cquantity = ArmorBag.objects.filter(character=character.id, armor=item.id).first()
                    current_durability = Cquantity.current_durability
                    item_type = "armor"

                item_data.append({
                    "id": item.id,
                    "name": item.name,
                    "type": item_type,
                    "repair_cost": item.repair_cost,
                    "max_durability": item.max_durability,
                    "current_durability": current_durability,
                })

            return JsonResponse({'message': "Repair", 'items': item_data}, status=200)
        elif message == "upgrade":
            items = list(character.weapons.all()) + list(character.armor.all())
            item_data = [
                {
                    "id": item.id,
                    "name": item.name,
                    "damage": item.damage if hasattr(item, 'damage') else None,
                    "defense": item.defense if hasattr(item, 'defense') else None,
                    "upgradedDefense": item.defense + 2 if hasattr(item, 'defense') else None,
                    "ingredients": [
                        {"name": ingredient.item.name, "quantity": ingredient.quantity}
                        for ingredient in item.equipablesingredients_set.all()
                    ] if hasattr(item, 'crafting_ingredients') else None,
                    "weaponLevel": {
                        "current_level": (
                            item.weaponbag_set.filter(character_id=character.id).first().current_level
                            if item.weaponbag_set.exists() else None
                        ),
                    } if isinstance(item, Weapon) and hasattr(item, "weaponbag_set") else None,
                    "armorLevel": {
                        "current_level": (
                            item.armorbag_set.filter(character_id=character.id).first().current_level
                            if item.armorbag_set.exists() else None
                        ),
                    } if isinstance(item, Armor) and hasattr(item, "armorbag_set") else None,

                    'updatedDam': {
                        "upgraded_damage": (
                            item.weaponbag_set.filter(character_id=character.id).first().upgraded_damage
                            if item.weaponbag_set.exists() else None
                        ),
                    } if isinstance(item, Weapon) and hasattr(item, "weaponbag_set") else None,

                    'updatedDen': {
                        "upgraded_defense": (
                            item.armorbag_set.filter(character_id=character.id).first().upgraded_defense
                            if item.armorbag_set.exists() else None
                        ),
                    } if isinstance(item, Armor) and hasattr(item, "armorbag_set") else None,

                    "upgradedDamage": item.damage + 2 if hasattr(item, 'damage') else None,
                }
                for item in items
            ]
            ingredients = [
                {"id": item.item_id,
                 "name": item.item.name,
                 "quantity": item.quantity}
                for item in backpack
                if hasattr(item.item, "forgeIngredient")
            ]

            # print(item_data)

            return JsonResponse({'message': "Repair", 'items': item_data, 'ingredients': ingredients}, status=200)

    elif request.method == "POST":
        message = request.headers.get('X-Custom-Message')
        userName = request.headers.get('X-Custom-User')
        user = CustomUser.objects.get(username=userName)
        character = user.character
        if message == "smelt":
            data = json.loads(request.body.decode('utf-8'))
            item = data.get('OreId')
            itemName = data.get('OreName')
            Ingot = itemName.replace("Ore", "Ingot")
            Ore = BackpackItem.objects.filter(item_id=item).first()
            if Ore:
                Ore.quantity = Ore.quantity - 2
                Ore.save()
                addItemToBag(Ingot, userName)
                return JsonResponse({'message': 'Completed'}, status=200)

        elif message == "forge":
            data = json.loads(request.body.decode('utf-8'))
            # item = data.get('itemId')
            itemName = data.get('itemName')
            weapon_exists = Weapon.objects.filter(name=itemName).exists()
            armor_exists = Armor.objects.filter(name=itemName).exists()

            if weapon_exists:
                result = addWeapon(itemName, character)
                print(result)
                return result

            elif armor_exists:
                result = addArmor(itemName, character)
                print(result)
                return result

        elif message == "repair":
            data = json.loads(request.body.decode('utf-8'))
            itemName = data.get('name')
            itemType = data.get('type')
            itemCost = data.get('repair_cost')
            itemId = data.get('itemId')
            if itemType == 'weapon':
                weapon = character.weapons.get(name=itemName)
                weaponBag = WeaponBag.objects.filter(character=character.id, weapon=itemId).first()

                weaponBag.current_durability = weapon.max_durability
                if character.gold - itemCost < 0:
                    return JsonResponse({"message": "Insufficient funds"}, status=200)
                else:
                    character.gold = character.gold - itemCost
                    weaponBag.save()
                    character.save()
                    sendData = {
                        "newDur": weaponBag.current_durability,
                        "maxDur": weapon.max_durability

                    }

                    return JsonResponse({"message": "item repaired", "data": sendData}, status=200)
            elif itemType == 'armor':
                armor = character.armor.get(name=itemName)
                armorBag = ArmorBag.objects.filter(character=character.id, armor=itemId).first()

                armorBag.current_durability = armor.max_durability
                if character.gold - itemCost < 0:
                    return JsonResponse({"message": "Insufficient funds"}, status=200)
                else:
                    character.gold = character.gold - itemCost
                    armorBag.save()
                    character.save()
                    sendData = {
                        "newDur": armorBag.current_durability,
                        "maxDur": armor.max_durability

                    }
                    return JsonResponse({"message": "item repaired", "data": sendData}, status=200)

        elif message == "upgrade":
            data = json.loads(request.body.decode('utf-8'))
            itemName = data.get('item')
            id = data.get('itemId')
            heldIngredients = BackpackItem.objects.filter(character_id=character.id)
            if Weapon.objects.filter(name=itemName).first():
                weapon = character.weapons.get(name=itemName)
                weaponBag = WeaponBag.objects.filter(character=character.id, weapon=weapon.id).first()
                # print(heldIngredients)
                ingredients = equipablesIngredients.objects.filter(weapon_id=weapon.id)
                for ingredient in ingredients:
                    item = BackpackItem.objects.get(item_id=ingredient.item_id, character_id=character.id)
                    # print(item)
                    if item:
                        if item.quantity - ingredient.quantity < 0:
                            return JsonResponse({'message': f"Missing or insufficient quantity for {item.item.name}"})
                        else:
                            item.quantity = item.quantity - ingredient.quantity
                            item.save()

                weaponBag.current_level = weaponBag.current_level + 1
                if weaponBag.upgraded_damage == 0:
                    weaponBag.upgraded_damage = weapon.damage
                else:
                    weaponBag.upgraded_damage = weaponBag.upgraded_damage + 2
                weaponBag.save()
                return JsonResponse({'message': "Weapon upgraded"}, status=200)
            elif Armor.objects.filter(name=itemName).first():
                armor = character.armor.get(name=itemName)
                armorBag = ArmorBag.objects.filter(character=character.id, armor=armor.id).first()
                # print(heldIngredients)
                ingredients = equipablesIngredients.objects.filter(armor_id=armor.id)
                for ingredient in ingredients:
                    item = BackpackItem.objects.get(item_id=ingredient.item_id, character_id=character.id)
                    if item:
                        if item.quantity - ingredient.quantity < 0:
                            return JsonResponse({'message': f"Missing or insufficient quantity for {item.item.name}"})
                        else:
                            item.quantity = item.quantity - ingredient.quantity
                            item.save()
                armorBag.current_level = armorBag.current_level + 1
                if armorBag.upgraded_defense == 0:
                    armorBag.upgraded_defense = armor.defense
                else:
                    armorBag.upgraded_defense = armorBag.upgraded_defense + 2
                armorBag.save()
                return JsonResponse({'message': "Armor upgraded"}, status=200)


# may not need
@login_required
def healthMotivation(request, username):
    return JsonResponse({'message': "Hi"})


# may not need

@login_required
def ironsteadPage(request, username):
    return render(request, "ironstead.html")


@login_required
def trainingView(request, username):
    user = CustomUser.objects.get(username=username)
    character = user.character
    weapon_bag = WeaponBag.objects.filter(character_id=character.id).first()
    if weapon_bag:
        weapon_name = weapon_bag.weapon.name
        weapon_data = {
            'weapon_name': weapon_name,
            'weapon_id': weapon_bag.weapon_id
        }
    else:
        weapon_data = {}
    skills = Skill.objects.all()
    magic = magicTome.objects.all()
    magicJson = json.loads(serialize('json', magic))
    magicData = [item['fields'] for item in magicJson]
    return render(request, "ironsteadTraining.html", {'user': user, "character": character, "weapon": weapon_data,
                                                      "skills": skills, "magic": magicData})


@login_required
def trainingGrab(request, username):
    if request.method == "GET":
        message = request.headers.get('X-Custom-Message')
        userName = request.headers.get('X-Custom-User')
        user = CustomUser.objects.get(username=userName)
        character = user.character
        skill = Skill.objects.filter(name=message).first()
        try:
            weapon = WeaponBag.objects.filter(weapon_id=message, character_id=character.id)
        except ValueError:
            weapon = None
        magic = Magic.objects.filter(name=message).first() # need to change to magicTome

        if skill:
            skill = {"name": skill.name, "description": skill.description, 'level_required': skill.level_required,
                     'skill_type': skill.skill_type,
                     'damage': skill.damage, 'max_damage': skill.max_damage, 'healing': skill.healing,
                     'max_healing': skill.max_healing}

            skillName = Skill.objects.get(name=message)
            skillset = skillSet.objects.filter(skill_id=skillName.id, character_id=character.id)
            if skillset:
                skillsetJson = json.loads(serialize('json', skillset))
                skillsetData = skillsetJson[0]['fields']
                return JsonResponse({"skill": skill, "skillSet": skillsetData})
            else:
                return JsonResponse({"skill": skill})
        elif weapon:
            weaponJson = json.loads(serialize('json', weapon))
            weaponBagData = weaponJson[0]['fields']
            weapon_id = weaponBagData['weapon']
            weaponModel = Weapon.objects.get(id=weapon_id)
            data = {
                "weapon_name": weaponModel.name,
                "weapon_desc": weaponModel.description,
            }
            return JsonResponse({"weaponBag": weaponBagData, "data": data})
        elif magic:
            magicData = {
                "name": magic.name,
                "desc": magic.description,
                "damage": magic.damage,
                "healing": magic.healing
            }
            return JsonResponse({"magic": magicData})

        else:
            return JsonResponse({"message": message})

    elif request.method == "POST":
        message = request.headers.get('X-Custom-Message')
        userName = request.headers.get('X-Custom-User')
        user = CustomUser.objects.get(username=userName)
        character = user.character
        if message == "skill":
            data = json.loads(request.body.decode('utf-8'))
            message = data.get('message')
            skill = Skill.objects.get(name=message)
            result = addSkill(skill, character)
            character.current_motivation = character.current_motivation - 1
            character.save()
            if result == "Max Efficiency":
                return JsonResponse({"message": "skill is maxed out"})
            else:
                return JsonResponse(
                    {'message': "Skill received", "result": result, "currentMotivation": character.current_motivation,
                     "maxMotivation": character.motivation})

        elif message == "weapon":
            data = json.loads(request.body.decode('utf-8'))
            name = data.get('name')
            type = data.get('trainType')
            weapon = Weapon.objects.get(name=name)
            weapon_bag = WeaponBag.objects.get(character_id=character.id, weapon_id=weapon.id)
            result = practiceWeapon(weapon, weapon_bag, character, type)
            if result == 1:  # 0.25
                message = "Failure is the stepping stones to success!"
            elif result == 2:  # 0.50
                message = "I can do anything I put my mind too!"
            elif result == 3:  # 1
                message = "I will win, even if it costs my life!"

            if character.current_health <= 0:
                return JsonResponse({'message': "You died", 'redirect': reverse('deadView', kwargs={'username': userName})})
            return JsonResponse({"message": message, "currentMotivation": character.current_motivation,
                                 "currentHealth": character.current_health, "maxHealth": character.health,
                                 "maxMotivation": character.motivation, 'efficiency': weapon_bag.weapon_efficiency})

        elif message == "magic":
            data = json.loads(request.body.decode('utf-8'))
            name = data.get('name')
            type = data.get('trainType')
            magic = Magic.objects.get(name=name)
            magic_tome = magicTome.objects.get(character_id=character.id, magic_id=magic.id)
            result = practiceMagic(magic, magic_tome, character, type)
            if result == 1:  # 0.25
                message = "Failure is the stepping stones to success!"
            elif result == 2:  # 0.50
                message = "I can do anything I put my mind too!"
            elif result == 3:  # 1
                message = "I will win, even if it costs my life!"

            if character.current_health <= 0:
                return JsonResponse({'message': "You died", 'redirect': reverse('deadView', kwargs={'username': userName})})
            return JsonResponse({"message": message, "currentMotivation": character.current_motivation,
                                 "currentHealth": character.current_health, "maxHealth": character.health,
                                 "maxMotivation": character.motivation, 'efficiency': magic_tome.weapon_efficiency})
        else:
            return JsonResponse({'message': "POST"})















# deadView
def deadView(request, username):
    return render(request, 'deadView.html')


