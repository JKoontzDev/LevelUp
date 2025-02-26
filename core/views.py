from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from asgiref.sync import sync_to_async
from core.models import *
from django.http import JsonResponse, HttpResponseRedirect
import json
import random
from django.db.models import F
from datetime import datetime


@sync_to_async(thread_sensitive=True)
def get_user_character(username):
    try:
        user = CustomUser.objects.select_related('character__rank').get(username=username)
        character = user.character

        return user, character
    except CustomUser.DoesNotExist:
        return None, None


@sync_to_async(thread_sensitive=True)
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


@sync_to_async(thread_sensitive=True)
def get_random_quests(num_quests, username):
    user = CustomUser.objects.get(username=username)
    character = user.character
    Quest = dailyQuest.objects.all()
    dQuest = list(Quest)
    random_quests = random.sample(dQuest, num_quests)
    character.quests.add(*random_quests)
    character.save()
    return random_quests


@sync_to_async(thread_sensitive=True)
def named_drops(drop):
    items = Item.objects.filter(id__in=drop)
    id_to_name = {item.id: item.name for item in items}
    names = [id_to_name.get(item_id, "Unknown") for item_id in drop]
    return names


@sync_to_async
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


@sync_to_async
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


@sync_to_async
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


@sync_to_async(thread_sensitive=True)
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


@sync_to_async(thread_sensitive=True)
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


@sync_to_async(thread_sensitive=True)
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


def load_serial(type):
    Json = json.loads(serialize('json', type))
    Data = [item['fields'] for item in Json]
    print(Data)
    return Data


@sync_to_async
def get_last_four_items(character):
    listt = list(BackpackItem.objects.filter(character=character).order_by('-id')[:4])
    backpack_items_data = []
    for item in listt:
        backpack_items_data.append({
            'item_name': item.item.name,
        })
    return backpack_items_data


@sync_to_async
def get_backpack_data(character_id, route):
    if route == "blacksmith":
        result = list(BackpackItem.objects.filter(
            character_id=character_id,
            item__forgeIngredient=True,
        ))
        backpack_data = [
            {
                "id": item.item_id,
                "name": item.item.name,
                "quantity": item.quantity,
            }
            for item in result
        ]
        return backpack_data
    else:
        result = list(BackpackItem.objects.filter(
            character_id=character_id,
        ))
        backpack_data = [
            {
                "id": item.item_id,
                "name": item.item.name,
                "quantity": item.quantity,
            }
            for item in result
        ]
        return backpack_data


@sync_to_async
def get_magic_data(character_id):
    result = list(magicTome.objects.filter(
        character_id=character_id,
    ))
    magic_data = [
        {
            "id": item.magic_id,
            "name": item.magic.name,
        }
        for item in result
    ]
    return magic_data


@sync_to_async
def get_skills_data(character_id):
    result = list(skillSet.objects.filter(
        character_id=character_id,
    ))
    skill_data = [
        {
            "id": item.skill_id,
            "name": item.skill.name,
        }
        for item in result
    ]
    return skill_data


@sync_to_async
def forgeableFun(armors, weapons, backpack):
    print(backpack)
    forgeables = []
    for item in weapons + armors:
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
    return forgeables





# routes

def homePage(request):
    return render(request, template_name="home.html")


async def loginPage(request):
    if request.method == "POST":
        form = loginForm(data=request.POST or None)
        RegForm = CustomUserCreationForm(data=request.POST or None)
        is_valid_reg = await sync_to_async(RegForm.is_valid)()
        is_valid_login = await sync_to_async(form.is_valid)()
        if is_valid_login:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = await sync_to_async(authenticate)(request, username=username, password=password)
            if user is not None:
                await sync_to_async(login)(request, user)
                return redirect('dashboard', username=username)
        if is_valid_reg:
            await sync_to_async(RegForm.save)()
            username = RegForm.cleaned_data['username']
            password = RegForm.cleaned_data['password1']
            user = await sync_to_async(authenticate)(request, username=username, password=password)
            if user is not None:
                await sync_to_async(login)(request, user)
                rank = await Rank.objects.aget(name="Weak")
                user1 = await CustomUser.objects.aget(username=username)
                new_character = await Character.objects.acreate(character_name=username)
                character = await Character.objects.aget(character_name=username)
                character.rank = rank
                user1.character = new_character
                await sync_to_async(user1.save)()
                await sync_to_async(character.save)()
                return redirect('dashboard', username=username)
        else:
            #print(RegForm.errors)
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
async def dashboardPage(requests, username):
    user, character = await get_user_character(username)
    if user.base_number_of_quests > 0:
        user.weekly_quests_count = user.base_number_of_quests * 7
        await sync_to_async(user.save)()
    last_four_items = await get_last_four_items(character)
    number_of_quests = user.number_of_quests
    if requests.method == "POST":
        data = json.loads(requests.body.decode('utf-8'))
        message = data.get('message')
        if message == 'Finish task!':  # takes the looped Json from finished_task_route
            NumberQuests = data.get('NumberQuest')
            questID = data.get('questID')
            # print(f"change_noq is {NumberQuests}")
            user.number_of_quests = NumberQuests
            quest_to_remove = await sync_to_async(character.quests.filter(id=questID).first)()
            await sync_to_async(character.quests.remove)(quest_to_remove)
            await sync_to_async(user.save)()
            await sync_to_async(character.save)()
            new_num_quests = user.number_of_quests
            return JsonResponse(
                {"message": "Task completed successfully from dashboard!", "newNumQuest": new_num_quests}, status=200)
        elif message == 'Get quest details!':  # gets quest details from frontend
            data = json.loads(requests.body.decode('utf-8'))
            quests = data.get('quests')
            fetchedQuest = await sync_to_async(list)(dailyQuest.objects.filter(quest_name__in=quests))
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
                dquest = await sync_to_async(list)(character.quests.all())
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
                await sync_to_async(character.quests.clear)()
                user.gotten_quests = True
                await sync_to_async(user.save)()
                dquest = await get_random_quests(number_of_quests, username)
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
async def finish_task_route(request, username):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        task_index = data.get('taskIndex')

        task_complete = await finish_task(task_index, username)  # sends to function

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
        named_drop = await named_drops(drops)
        # db query
        completedQuest = await dailyQuest.objects.aget(quest_name=questName)
        user = await CustomUser.objects.aget(username=username)
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
        print(send_out)
        return JsonResponse(send_out, status=200)


@login_required
async def characterPage(request, username):
    user, character = await get_user_character(username)
    backpack = await get_backpack_data(character.id, "character")
    spellBook = await get_magic_data(character.id)
    skillset = await get_skills_data(character.id)
    return render(request, "character.html", {"user": user, "character": character, "backpack": backpack,
                                              "spellBook": spellBook, "skillSet": skillset})


@login_required
def worldMapPage(request, username):
    return render(request, "worldMap.html")


@login_required
async def marketView(request, username):
    user, character = await get_user_character(username)
    return render(request, "market.html", {'user': user, "character": character})


@login_required
async def marketViewSendItems(request, username):
    if request.method == "GET":
        items = await sync_to_async(list)(
            Item.objects.filter(marketable=True).order_by('?')
        )
        itemsToPage = []
        for item in items:
            if random.uniform(0, 100) <= item.market_drop_rate:
                itemsToPage.append({
                    'item': item.name,
                    'price': item.price,
                    'description': item.description,
                    'type': item.type,
                })
        return JsonResponse(itemsToPage, status=200, safe=False)

    elif request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        user_name = data.get('username')
        item_name = data.get('itemName')
        result = await sync_to_async(addItemToBag)(item_name, user_name)
        if result == 1:
            send_out = {"message": "Task completed successfully!", "item": item_name}
            return JsonResponse(send_out, status=200)
        else:
            send_out = {"message": "Insufficient funds", "item": item_name}
            return JsonResponse(send_out, status=200)


@login_required
async def blackSmithView(request, username):
    user, character = await get_user_character(username)
    return render(request, "blackSmith.html", {'user': user, "character": character})


@login_required
async def blackSmithFetch(request, username):
    if request.method == "GET":
        message = request.headers.get('X-Custom-Message')
        userName = request.headers.get('X-Custom-User')
        user, character = await get_user_character(userName)
        backpack = await get_backpack_data(character.id, 'blacksmith')


        if message == "smelt":
            filtered_backpack_data = [
                item for item in backpack if "ore" in item["name"].lower()
            ]
            if not filtered_backpack_data:
                return JsonResponse({'message': 'Completed'}, status=200)
            else:
                return JsonResponse({'message': 'Completed', 'backpack': filtered_backpack_data}, status=200)
        elif message == "forge":
            weapons = await sync_to_async(list)(Weapon.objects.filter(forgeable=True))
            armors = await sync_to_async(list)(Armor.objects.filter(forgeable=True))
            forgeables = await forgeableFun(armors, weapons, backpack)
            if not backpack:
                return JsonResponse({'message': 'Forge', "forgeables": forgeables}, status=200)
            else:
                return JsonResponse({'message': 'Forge', "items": backpack, "forgeables": forgeables}, status=200)
        elif message == "repair":
            items = [item async for item in character.weapons.all()] + [item async for item in character.armor.all()]
            print(items)
            item_data = []

            for item in items:
                if isinstance(item, Weapon):
                    Cquantity = await WeaponBag.objects.filter(character=character.id, weapon=item.id).afirst()
                    current_durability = Cquantity.current_durability
                    item_type = "weapon"
                elif isinstance(item, Armor):
                    Cquantity = await ArmorBag.objects.filter(character=character.id, armor=item.id).afirst()
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
                print(item_data)

            return JsonResponse({'message': "Repair", 'items': item_data}, status=200)
        elif message == "upgrade":
            items = [item async for item in character.weapons.all()] + [item async for item in character.armor.all()]

            item_data = [
                {
                    "id": item.id,
                    "name": item.name,
                    "damage": item.damage if hasattr(item, 'damage') else None,
                    "defense": item.defense if hasattr(item, 'defense') else None,
                    "upgradedDefense": item.defense + 2 if hasattr(item, 'defense') else None,
                    "ingredients": [
                        {"name": ingredient.item.name, "quantity": ingredient.quantity}
                        async for ingredient in item.equipablesingredients_set.select_related("item").all()
                    ] if hasattr(item, "equipablesingredients_set") else None,
                    "weaponLevel": {
                        "current_level": (
                                (weapon := await item.weaponbag_set.filter(character_id=character.id).afirst())
                                and weapon.current_level
                        ) if isinstance(item, Weapon) and hasattr(item, "weaponbag_set") else None,
                    },
                    "armorLevel": {
                        "current_level": (
                                (armor := await item.armorbag_set.filter(character_id=character.id).afirst())
                                and armor.current_level
                        ) if isinstance(item, Armor) and hasattr(item, "armorbag_set") else None,
                    },
                    "updatedDam": {
                        "upgraded_damage": (
                                (weapon := await item.weaponbag_set.filter(character_id=character.id).afirst())
                                and weapon.upgraded_damage
                        ) if isinstance(item, Weapon) and hasattr(item, "weaponbag_set") else None,
                    },
                    "updatedDen": {
                        "upgraded_defense": (
                                (armor := await item.armorbag_set.filter(character_id=character.id).afirst())
                                and armor.upgraded_defense
                        ) if isinstance(item, Armor) and hasattr(item, "armorbag_set") else None,
                    },
                    "upgradedDamage": item.damage + 2 if hasattr(item, 'damage') else None,
                }
                for item in items
            ]

            #print(item_data)

            return JsonResponse({'message': "Repair", 'items': item_data, 'ingredients': backpack}, status=200)

    elif request.method == "POST":
        message = request.headers.get('X-Custom-Message')
        userName = request.headers.get('X-Custom-User')
        user, character = await get_user_character(userName)
        if message == "smelt":
            data = json.loads(request.body.decode('utf-8'))
            item = data.get('OreId')
            itemName = data.get('OreName')
            Ingot = itemName.replace("Ore", "Ingot")
            Ore = await BackpackItem.objects.filter(item_id=item).afirst()
            if Ore:
                Ore.quantity = Ore.quantity - 2
                await sync_to_async(Ore.save)()
                await addItemToBag(Ingot, userName)
                return JsonResponse({'message': 'Completed'}, status=200)

        elif message == "forge":
            data = json.loads(request.body.decode('utf-8'))
            # item = data.get('itemId')
            itemName = data.get('itemName')
            weapon_exists = await Weapon.objects.filter(name=itemName).aexists()
            armor_exists = await Armor.objects.filter(name=itemName).aexists()

            if weapon_exists:
                result = await addWeapon(itemName, character)
                print(result)
                return result

            elif armor_exists:
                result = await addArmor(itemName, character)
                print(result)
                return result

        elif message == "repair":
            data = json.loads(request.body.decode('utf-8'))
            itemName = data.get('name')
            itemType = data.get('type')
            itemCost = data.get('repair_cost')
            itemId = data.get('itemId')
            if itemType == 'weapon':
                weapon = await character.weapons.aget(name=itemName)
                weaponBag = await WeaponBag.objects.filter(character=character.id, weapon=itemId).afirst()

                weaponBag.current_durability = weapon.max_durability
                if character.gold - itemCost < 0:
                    return JsonResponse({"message": "Insufficient funds"}, status=200)
                else:
                    character.gold = character.gold - itemCost
                    await sync_to_async(weaponBag.save)()
                    await sync_to_async(character.save)()
                    sendData = {
                        "newDur": weaponBag.current_durability,
                        "maxDur": weapon.max_durability

                    }

                    return JsonResponse({"message": "item repaired", "data": sendData}, status=200)
            elif itemType == 'armor':
                armor = await character.armor.aget(name=itemName)
                armorBag = await ArmorBag.objects.filter(character=character.id, armor=itemId).afirst()

                armorBag.current_durability = armor.max_durability
                if character.gold - itemCost < 0:
                    return JsonResponse({"message": "Insufficient funds"}, status=200)
                else:
                    character.gold = character.gold - itemCost
                    await sync_to_async(armorBag.save)()
                    await sync_to_async(character.save)()
                    sendData = {
                        "newDur": armorBag.current_durability,
                        "maxDur": armor.max_durability

                    }
                    return JsonResponse({"message": "item repaired", "data": sendData}, status=200)

        elif message == "upgrade":
            data = json.loads(request.body.decode('utf-8'))
            itemName = data.get('item')
            id = data.get('itemId')
            #heldIngredients = BackpackItem.objects.filter(character_id=character.id)
            if await Weapon.objects.filter(name=itemName).afirst():
                weapon = await character.weapons.aget(name=itemName)
                weaponBag = await WeaponBag.objects.filter(character=character.id, weapon=weapon.id).afirst()
                # print(heldIngredients)
                ingredients = await sync_to_async(list)(equipablesIngredients.objects.filter(weapon_id=weapon.id))
                for ingredient in ingredients:
                    item = await BackpackItem.objects.aget(item_id=ingredient.item_id, character_id=character.id)
                    # print(item)
                    if item:
                        if item.quantity < ingredient.quantity - 1:
                            item_name = await Item.objects.aget(id=ingredient.item_id)
                            return JsonResponse({'message': f"Missing or insufficient quantity for {item_name}"})
                        else:
                            item.quantity = item.quantity - (ingredient.quantity - 1)
                            await sync_to_async(item.save)()

                weaponBag.current_level = weaponBag.current_level + 1
                if weaponBag.upgraded_damage == 0:
                    weaponBag.upgraded_damage = weapon.damage
                else:
                    weaponBag.upgraded_damage = weaponBag.upgraded_damage + 2
                await sync_to_async(weaponBag.save)()
                return JsonResponse({'message': "Weapon upgraded"}, status=200)
            elif await Armor.objects.filter(name=itemName).afirst():
                armor = await character.armor.aget(name=itemName)
                armorBag = await ArmorBag.objects.filter(character=character.id, armor=armor.id).afirst()
                # print(heldIngredients)
                ingredients = await sync_to_async(list)(equipablesIngredients.objects.filter(armor_id=armor.id))
                for ingredient in ingredients:
                    print(ingredient.item_id)
                for ingredient in ingredients:
                    item = await BackpackItem.objects.aget(item_id=ingredient.item_id, character_id=character.id)
                    #print(ingredient)
                    if item:
                        print(item.quantity)
                        if item.quantity - (ingredient.quantity - 1) < 0:
                            item_name = await Item.objects.aget(id=ingredient.item_id)
                            return JsonResponse({'message': f"Missing or insufficient quantity for {item_name}"})
                        else:
                            item.quantity = item.quantity - (ingredient.quantity - 1)
                            await sync_to_async(item.save)()
                armorBag.current_level = armorBag.current_level + 1
                if armorBag.upgraded_defense == 0:
                    armorBag.upgraded_defense = armor.defense
                else:
                    armorBag.upgraded_defense = armorBag.upgraded_defense + 2
                await sync_to_async(armorBag.save)()
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
async def trainingView(request, username):
    user, character = await get_user_character(username)
    weapon_bag = await sync_to_async(WeaponBag.objects.filter(character_id=character.id).first)()
    if weapon_bag:
        weapon = await sync_to_async(Weapon.objects.get)(id=weapon_bag.weapon_id)
        weapon_name = weapon.name
        weapon_data = {
            'weapon_name': weapon_name,
            'weapon_id': weapon_bag.weapon_id
        }
    else:
        weapon_data = {}
    skills = await sync_to_async(list)(Skill.objects.all())
    magic_tome = await sync_to_async(magicTome.objects.filter(character_id=character.id).first)()
    if magic_tome:
        magic = await sync_to_async(Magic.objects.get)(id=magic_tome.magic_id)
        spell_name = magic.name
        magic_data = {
            'spell_name': spell_name,
            'spell_id': magic_tome.magic_id
        }
    else:
        magic_data = {}
    return render(request, "ironsteadTraining.html", {'user': user, "character": character, "weapon": weapon_data,
                                                      "skills": skills, "magic": magic_data})



@login_required
async def trainingGrab(request, username):
    if request.method == "GET":
        message = request.headers.get('X-Custom-Message')
        userName = request.headers.get('X-Custom-User')
        user, character = await get_user_character(userName)
        skill = await Skill.objects.filter(name=message).afirst()
        try:
            weapon = await sync_to_async(list)(WeaponBag.objects.filter(weapon_id=message, character_id=character.id))
            magic = await sync_to_async(list)(magicTome.objects.filter(magic_id=message, character_id=character.id))

        except ValueError:
            None, None


        if skill:
            skill = {"name": skill.name, "description": skill.description, 'level_required': skill.level_required,
                     'skill_type': skill.skill_type,
                     'damage': skill.damage, 'max_damage': skill.max_damage, 'healing': skill.healing,
                     'max_healing': skill.max_healing}

            skillName = await Skill.objects.aget(name=message)
            skillset = await sync_to_async(list)(skillSet.objects.filter(skill_id=skillName.id, character_id=character.id))
            if skillset:
                result = load_serial(skillset)
                return JsonResponse({"skill": skill, "skillSet": result})
            else:
                return JsonResponse({"skill": skill, "skillSet": {}})
        elif weapon:
            result = await sync_to_async(load_serial)(weapon)
            weapon_id = result[0]['weapon']
            weaponModel = await Weapon.objects.aget(id=weapon_id)
            data = {
                "weapon_name": weaponModel.name,
                "weapon_desc": weaponModel.description,
            }
            return JsonResponse({"weaponBag": result, "data": data})
        elif magic:
            result = await sync_to_async(load_serial)(magic)
            magic_id = result[0]['magic']
            magicModel = await Magic.objects.aget(id=magic_id)
            data = {
                "magic_name": magicModel.name,
                "magic_desc": magicModel.description,
            }
            return JsonResponse({"magic": result, "magicTome": data})

        else:
            return JsonResponse({"message": message})

    elif request.method == "POST":
        message = request.headers.get('X-Custom-Message')
        userName = request.headers.get('X-Custom-User')
        user, character = await get_user_character(userName)
        if message == "skill":
            data = json.loads(request.body.decode('utf-8'))
            message = data.get('message')
            skill = await Skill.objects.aget(name=message)
            result = await addSkill(skill, character)
            character.current_motivation = character.current_motivation - 1
            await sync_to_async(character.save)()
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
            weapon = await Weapon.objects.aget(name=name)
            weapon_bag = await WeaponBag.objects.aget(character_id=character.id, weapon_id=weapon.id)
            result = await practiceWeapon(weapon, weapon_bag, character, type)
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
            magic = await Magic.objects.aget(name=name)
            magic_tome = await magicTome.objects.aget(character_id=character.id, magic_id=magic.id)
            result = await practiceMagic(magic, magic_tome, character, type)
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
                                 "maxMotivation": character.motivation, 'efficiency': magic_tome.spell_efficiency})
        else:
            return JsonResponse({'message': "POST"})















# deadView
def deadView(request, username):
    return render(request, 'deadView.html')


