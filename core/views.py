from django.shortcuts import render, redirect, get_object_or_404
#from django.urls import reverse
import requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.core.cache import cache
from .forms import *
#from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.serializers import serialize
from django.urls import reverse
from django.db.models import Q
from django.db import transaction
from asgiref.sync import sync_to_async
from core.models import *
from django.http import JsonResponse, HttpResponseBadRequest
import json
import random
from uuid import uuid4
#from django.db.models import F
#from datetime import datetime
import pillow_heif
from PIL import Image
import os
from LevelUp.settings import MEDIA_ROOT
import httpx
import asyncio
from collections import defaultdict



ollama_warmed_up = False
ollama_lock = asyncio.Lock()


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
    #if character.can_advance_rank():
    #    character.advance_rank()
    #    character.save()
    # start daily dungeon raid and level up/ gain exp
    messageBoard = ""
    user.target_num_quests_inc = user.target_num_quests_inc + 1
    if user.target_num_quests_inc == user.target_num_quests:
        user.completed_days += 1
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
    Quest = taskModel.objects.get(quest_name=index)
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
    user = CustomUser.objects.select_related("character") \
                             .get(username=username)
    u_tasks = list(taskModel.objects.filter(creator=user.id))
    everyday = [t for t in u_tasks if t.frequency == "everyday"]
    random_defined = [t for t in u_tasks if t.frequency == "random"]


    # Ensure base_number is up to date
    if len(everyday) > user.base_number_of_quests:
        user.base_number_of_quests = len(everyday)
        user.save()

    needed = user.base_number_of_quests - len(everyday)
    final = everyday.copy()

    # Fill from random_defined, then system, then fallback to num_quests
    if needed > 0:
        pick_from_defined = min(len(random_defined), needed)
        final.extend(random.sample(random_defined, pick_from_defined))
        needed -= pick_from_defined

    if needed > 0:
        system = list(taskModel.objects.filter(source='system'))
        pick_from_system = min(len(system), needed)
        final.extend(random.sample(system, pick_from_system))
        needed -= pick_from_system

    # If user had no definitions at all, override
    if not u_tasks:
        system = list(taskModel.objects.filter(source='system'))
        final = random.sample(system, min(len(system), num_quests))

    # Persist once
    character = user.character
    character.quests.add(*final)
    character.save()
    return final


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


@sync_to_async
def bulkAddItemToBag(itemListToAdd, username):
    user = CustomUser.objects.get(username=username)
    character = user.character

    # Separate integers and strings
    item_ids = [drop for drop in itemListToAdd if isinstance(drop, int)]
    name_list_drops = [drop for drop in itemListToAdd if isinstance(drop, str)]

    # Get all matching Item objects
    items = list(Item.objects.filter(id__in=item_ids)) + list(Item.objects.filter(name__in=name_list_drops))

    # Create a dict to map both name and ID to the actual Item
    items_dict = {}
    for item in items:
        items_dict[item.id] = item
        items_dict[item.name] = item

    # Loop through the original drops and update backpack
    for drop in itemListToAdd:
        item = items_dict.get(drop)
        if item:
            backpack_item, created = BackpackItem.objects.get_or_create(character=character, item=item)
            if not created:
                backpack_item.quantity += 1
                backpack_item.save()

    return 1


def check_efficiency(efficiency, weapon_bag):
    if 4.0 <= efficiency < 5.0:
        weapon_bag.damage_modifier = weapon_bag.damage_modifier + 0.1
    elif efficiency == 10.0:
        weapon_bag.damage_modifier = weapon_bag.damage_modifier + 0.2
    weapon_bag.save()


def check_Magic_Efficiency(efficiency, magicTome, magic):
    if 4.0 <= efficiency < 5.0:
        if magic.damage != 0:
            magicTome.damage_modifier = magicTome.damage_modifier + 0.1
        elif magic.healing != 0:
            magicTome.healing_modifier = magicTome.healing_modifier + 0.1
    elif efficiency == 10.0:
        magicTome.damage_modifier = magicTome.damage_modifier + 0.2
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
                skillset.damage_modifier = skillset.damage_modifier + 0.1
            elif skill.healing != 0:
                skillset.healing_modifier = skillset.healing_modifier + 0.1
            skillset.save()
            return {"message": "LevelUp", "damage": skillset.damage_modifier, "efficiency": skillset.efficiency,
                    "healing": skillset.healing_modifier}
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
        skillset.efficiency = skillset.efficiency + 0.1
        skillset.save()
        return {"message": "LevelUp", "efficiency": skillset.efficiency}


@sync_to_async(thread_sensitive=True)
def practiceWeapon(weapon, weapon_bag, character, type):
    if type == 'safe':
        if weapon_bag.efficiency <= 5:
            num = random.randint(1, 100)
            if num >= 50:
                character.current_motivation = character.current_motivation - 1
                character.current_health = character.current_health - 1
                weapon_bag.efficiency = weapon_bag.efficiency + 0.25
                check_efficiency(weapon_bag.efficiency, weapon_bag)
                character.save()
                weapon_bag.save()
                return 1  # Damage
            else:
                character.current_motivation = character.current_motivation - 1
                weapon_bag.efficiency = weapon_bag.efficiency + 0.50
                check_efficiency(weapon_bag.efficiency, weapon_bag)
                character.save()
                weapon_bag.save()
                return 2  # good

        else:
            weapon_bag.efficiency = weapon_bag.efficiency + 0.50
            character.current_motivation = character.current_motivation - 1
            check_efficiency(weapon_bag.efficiency, weapon_bag)
            character.save()
            weapon_bag.save()
            return 2  # good
    elif type == 'intense':
        if weapon_bag.efficiency <= 5:
            num = random.randint(1, 100)
            if num >= 30:
                character.current_motivation = character.current_motivation - 1
                character.current_health = character.current_health - 2
                character.save()
                weapon_bag.save()
                return 1  # Damage
            else:
                character.current_motivation = character.current_motivation - 1
                weapon_bag.efficiency = weapon_bag.efficiency + 1
                check_efficiency(weapon_bag.efficiency, weapon_bag)
                character.save()
                weapon_bag.save()
                return 3  # amazing
        else:
            weapon_bag.efficiency = weapon_bag.efficiency + 1
            character.current_motivation = character.current_motivation - 1
            check_efficiency(weapon_bag.efficiency, weapon_bag)

            character.save()
            weapon_bag.save()
            return 3  # amazing


@sync_to_async(thread_sensitive=True)
def practiceMagic(magic, magic_tome, character, type):
    if type == 'safe':
        if magic_tome.efficiency <= 5:
            num = random.randint(1, 100)
            if num >= 50:
                character.current_motivation = character.current_motivation - 1
                character.current_health = character.current_health - 1
                magic_tome.efficiency = magic_tome.efficiency + 0.25
                check_Magic_Efficiency(magic_tome.efficiency, magic_tome, magic)
                character.save()
                magic_tome.save()
                return 1  # Damage
            else:
                character.current_motivation = character.current_motivation - 1
                magic_tome.efficiency = magic_tome.efficiency + 0.50
                check_Magic_Efficiency(magic_tome.efficiency, magic_tome, magic)
                character.save()
                magic_tome.save()
                return 2  # good

        else:
            magic_tome.efficiency = magic_tome.efficiency + 0.50
            character.current_motivation = character.current_motivation - 1
            check_Magic_Efficiency(magic_tome.efficiency, magic_tome, magic)
            character.save()
            magic_tome.save()
            return 2  # good
    elif type == 'intense':
        if magic_tome.efficiency <= 5:
            num = random.randint(1, 100)
            if num >= 30:
                character.current_motivation = character.current_motivation - 1
                character.current_health = character.current_health - 2
                character.save()
                return 1  # Damage
            else:
                character.current_motivation = character.current_motivation - 1
                magic_tome.efficiency = magic_tome.efficiency + 1
                check_Magic_Efficiency(magic_tome.efficiency, magic_tome, magic)
                character.save()
                magic_tome.save()
                return 3  # amazing
        else:
            magic_tome.efficiency = magic_tome.efficiency + 1
            character.current_motivation = character.current_motivation - 1
            check_Magic_Efficiency(magic_tome.efficiency, magic_tome, magic)
            character.save()
            magic_tome.save()
            return 3  # amazing


def load_serial(type):
    Json = json.loads(serialize('json', type))
    Data = [item['fields'] for item in Json]
    #print(Data)
    return Data


def handle_user_avatar_upload(user, user_avatar):
    file = user_avatar.name
    ext = os.path.splitext(file)[1].lower()
    if ext not in ['.png', '.jpg', '.jpeg']:
        raise ValidationError("Only PNG and JPEG formats are allowed for avatars.")

    try:
        image = Image.open(user_avatar)
        image.verify()
        user_avatar.seek(0)
        image = Image.open(user_avatar)

        if image.format not in ['PNG', 'JPEG']:
            raise ValidationError("Image content is not valid PNG or JPEG.")

    except Exception as e:
        raise ValidationError("Invalid image file.")

    filename = get_valid_filename(file)
    filename = f"{uuid4().hex}_{filename}"
    output_dir = os.path.join(MEDIA_ROOT, f"story_avatars/{user.id}")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, filename)

    with open(output_path, 'wb+') as destination:
        for chunk in user_avatar.chunks():
            destination.write(chunk)

    return os.path.join(f"story_avatars/{user.id}", filename)


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
                "description": item.item.description,
            }
            for item in result
        ]
        return backpack_data


@sync_to_async
def get_magic_data(character_id):
    result = list(magicTome.objects.filter(character_id=character_id))
    magic_data_list = []
    for item in result:
        magic_data = {
            "id": item.id,
            "name": item.magic.name,
            "description": item.magic.description,
            "damage": item.magic.damage,
            "healing": item.magic.healing,
            "damageModifier": item.damage_modifier,
            "healingModifier": item.healing_modifier,
            "efficiency": item.efficiency,
            "dexterity": item.dexterity
        }
        magic_data_list.append(magic_data)
    return magic_data_list


@sync_to_async
def get_weapons_equip(character_id, adventureQuest):
    if adventureQuest:
        queryset = WeaponBag.objects.filter(
            Q(current_equip=True) | Q(standby_weapon=True),
            character_id=character_id
        )
    else:
        queryset = WeaponBag.objects.filter(character_id=character_id)

    result = list(queryset)

    weapons_data = []
    for item in result:
        weapon_data = {
            "id": item.id,
            "name": item.weapon.name,
            "description": item.weapon.description,
            "damage": item.weapon.damage,
            "damageModifier": item.damage_modifier,
            "efficiency": item.efficiency
        }
        weapons_data.append(weapon_data)

    return weapons_data


@sync_to_async
def get_armor_equip(character_id, adventureQuest):
    if adventureQuest:
        queryset = ArmorBag.objects.filter(
            Q(current_equip=True) | Q(standby_armor=True),
            character_id=character_id
        )
    else:
        queryset = ArmorBag.objects.filter(character_id=character_id)

    result = list(queryset)
    armor_data_list = []
    #print(result)
    for item in result:
        armor_data = {
            "id": item.id,
            "name": item.armor.name,
            "description": item.armor.description,
            "defense": item.armor.defense,
            "defenseModifier": item.defense_modifier,
            "efficiency": item.efficiency,
            "dexterity": item.dexterity
        }
        armor_data_list.append(armor_data)

    return armor_data_list



@sync_to_async
def get_rank_data(character_id):
    character = Character.objects.get(id=character_id)
    rank = Rank.objects.get(name=character.rank)
    rank_details = rank.details
    data = {"name": rank.name,
            "description": rank_details.description,
            "attack": rank_details.attack,
            "damage": rank_details.damage}
    return data


@sync_to_async
def get_skills_data(character_id, adventureQuest):
    if adventureQuest:
        query = skillSet.objects.filter(character_id=character_id, skill__skill_type__in=[skillType.COMBAT, skillType.MAGIC, skillType.MOTIVATIONAL])
    else:
        query = skillSet.objects.filter(character_id=character_id)

    result = list(query)
    skills_data = []
    for item in result:
        skills_data.append({
            "id": item.id,
            "name": item.skill.name,
            "description": item.skill.description,
            "damage": item.skill.damage,
            "damage_modifier": item.damage_modifier,
            "healing": item.skill.healing,
            "healing_modifier": item.healing_modifier,
            "efficiency": item.efficiency,
            "dexterity": item.dexterity,
            "skill_type": item.skill.skill_type
        })
    return skills_data



@sync_to_async
def get_adventure_attack_info(attack):
    attack_data = {
        "id": attack.id,
        "name": attack.weapon.name,
        "description": attack.weapon.description,
        "damage": attack.weapon.damage,
        "damage_mod": attack.damage_modifier,
        "efficiency": attack.efficiency
    }
    return attack_data


@sync_to_async
def get_adventure_skill_info(skill):
    skills_data = {
        "id": skill.id,
        "name": skill.skill.name,
        "description": skill.skill.description,
        "damage": skill.skill.damage,
        "damage_modifier": skill.damage_modifier,
        "healing": skill.skill.healing,
        "healing_modifier": skill.healing_modifier,
        "efficiency": skill.efficiency,
        "dexterity": skill.dexterity
    }
    return skills_data


@sync_to_async
def get_adventure_rank_info(attack):
    rank_details = RankDetail.objects.get(attack=attack)
    data = {
            "description": rank_details.description,
            "attack": rank_details.attack,
            "damage": rank_details.damage}
    return data


@sync_to_async
def get_adventure_magic_info(attack):
    attack_data = {
        "id": attack.id,
        "name": attack.magic.name,
        "description": attack.magic.description,
        "damage": attack.magic.damage,
        "damage_mod": attack.damage_modifier,
        "healing": attack.magic.healing,
        "healing_mod": attack.healing_modifier,
        "efficiency": attack.efficiency,
        "dexterity": attack.dexterity
    }
    return attack_data


@sync_to_async
def get_adventure_defense_info(user):
    # get querysets for armor and character
    character = Character.objects.get(character_name=user)
    queryset_equip = ArmorBag.objects.filter(
        Q(current_equip=True),
        character_id=character.id
    )
    queryset_standby = ArmorBag.objects.filter(
        Q(standby_armor=True),
        character_id=character.id
    )
    # make list for for loop
    armor_equip = list(queryset_equip)
    armor_standby = list(queryset_standby)

    # get defense rating and modifier

    equipDefense = 0
    equipModifier = 0.0
    standbyDefense = 0
    standbyModifier = 0.0
    dexterity = character.dexterity

    for i in armor_equip:
        equipDefense += i.armor.defense
        equipModifier += i.defense_modifier
        dexterity += i.dexterity

    for i in armor_standby:
        standbyDefense += i.armor.defense
        standbyModifier += i.defense_modifier
        dexterity += i.dexterity


    data = {
        "equipDefense": equipDefense,
        "equipModifier": equipModifier,
        "standbyDefense": standbyDefense,
        "standbyModifier": standbyModifier,
        "dexterity": dexterity,
    }

    return data
    # LEFT OFF WITH DEFENSE/BLOCK/EVADE


@sync_to_async
def getEnemyData(enemy):
    enemyData = []
    enemy_objs = enemies.objects.filter(enemy_name__in=enemy).select_related('weapon', 'armor', 'magic')
    enemy_map = {e.enemy_name: e for e in enemy_objs}

    for name in enemy:
        enem = enemy_map.get(name)
        if enem is None:
            continue
        enemyData.append({
            "enemy_name": enem.enemy_name,
            "enemy_weapon_name": getattr(enem.weapon, 'name', None),
            "enemy_weapon_damage": getattr(enem.weapon, 'damage', 0),
            "enemy_weapon_speed": getattr(enem.weapon, 'attack_speed', 1),
            "enemy_weapon_critical": getattr(enem.weapon, 'critical_rate', 0),
            "enemy_armor": getattr(enem.armor, 'name', None),
            "enemy_armor_defense": getattr(enem.armor, 'defense', 0),
            "enemy_armor_resistance": getattr(enem.armor, 'resistance', 0),
            "enemy_magic": getattr(enem.magic, 'name', None),
            "enemy_magic_damage": getattr(enem.magic, 'damage', 0),
            "enemy_magic_special": getattr(enem.magic, 'special', None),
            "enemy_base_damage": enem.base_damage,
            "enemy_base_armor": enem.base_armor,
            "enemy_health": enem.health,
            "enemy_boss": enem.is_boss,
            "enemy_image": enem.image.url if enem.image else None,
            "enemy_gold": enem.gold_drop,
            "enemy_mana": enem.mana,
            "enemy_level": enem.level,
            "enemy_dexterity": enem.dexterity,
        })
    return enemyData


@sync_to_async
def forgeableFun(armors, weapons, backpack):
    #print(backpack)
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


npc_chat_locks = {}

async def get_npc_response(request, user_id, npc_name, player_input):
    key = f"{user_id}:{npc_name}"

    # Get or create semaphore for the current loop
    loop = asyncio.get_event_loop()
    if key not in npc_chat_locks or npc_chat_locks[key][0] != loop:
        npc_chat_locks[key] = (loop, asyncio.Semaphore(1))

    semaphore = npc_chat_locks[key][1]

    async with semaphore:
        model = "gemma:2b"
        try:
            # Retrieve chat history from session
            session_history = request.session.get("npc_chat_history", {})
            chat_history = session_history.get(key, [])

            # Get system prompt
            if npc_name == "ME":
                npc = await NPCS.objects.aget(name="ME")
                system_prompt = npc.prompt
            else:
                npc = await sync_to_async(NPCS.objects.get)(name=npc_name)
                system_prompt = await npc.generate_prompt(player_input)

            # Add system message only once
            if not any(msg["role"] == "system" for msg in chat_history):
                chat_history.insert(0, {
                    "role": "system",
                    "content": system_prompt
                })

            # Add user message
            chat_history.append({
                "role": "user",
                "content": player_input
            })

            # Call Ollama
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
                response = await client.post(
                    "http://127.0.0.1:11434/api/chat",
                    json={
                        "model": model,
                        "messages": chat_history,
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                npc_reply = result.get("message", {}).get("content", "").strip()

            # Add assistant response
            if npc_name == "ME":
                chat_history.append({
                    "role": "assistant",
                    "content": npc_reply
                })
            else:
                chat_history.append({
                    "role": f"{npc_name}",
                    "content": npc_reply
                })

            # Store back in session
            session_history[key] = chat_history[-30:]  # Trim for safety
            request.session["npc_chat_history"] = session_history
            request.session.modified = True

            return npc_reply or "NPC stays silent..."

        except asyncio.CancelledError:
            return f"{npc_name} didn't finish their thought..."
        except httpx.ReadTimeout:
            return f"{npc_name} is too busy to respond right now."
        except httpx.HTTPError:
            return f"Error talking to {npc_name}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"





@sync_to_async
def get_available_choices(scene_json, character):
    available = []
    for choice in scene_json.get("choices", []):
        reqs = choice.get("requirements", {})
        meets = True
        for key, value in reqs.items():
            if key.startswith("stats."):
                stat = key.split(".")[1]
                if getattr(character.stats, stat, 0) < value:
                    meets = False
            elif key == "inventory":
                for item in value:
                    if item not in character.inventory:
                        meets = False
        if meets:
            available.append(choice)
    return available


@sync_to_async
def getQuestGold(gold, character):
    #print(f"GOLD: {gold}; character gold:{character.gold}")
    character.gold = character.gold + gold
    character.save()


@sync_to_async
def equipItem(characterID, item):
    try:
        #print(f"Equip attempt for character {characterID} and item '{item}'")

        item_weapon = Weapon.objects.get(name=item)
        WeaponBag.objects.filter(character_id=characterID, current_equip=True).update(current_equip=False)

        weapon_bag = WeaponBag.objects.filter(character_id=characterID, weapon_id=item_weapon.id).first()
        if weapon_bag:
            weapon_bag.current_equip = True
            weapon_bag.save()
            return f"equip successful: {item_weapon.name}"
        else:
            return "Weapon not in bag"

    except Weapon.DoesNotExist:
        try:
            item_armor = Armor.objects.get(name=item)
            ArmorBag.objects.filter(character_id=characterID, current_equip=True).update(current_equip=False)

            armor_bag = ArmorBag.objects.filter(character_id=characterID, armor_id=item_armor.id).first()
            if armor_bag:
                armor_bag.current_equip = True
                armor_bag.save()
                return f"equip successful: {item_armor.name}"
            else:
                return "armor not in bag"

        except Armor.DoesNotExist:
            return "equip failed (item not found)"



# routes

def homePage(request):
    testaments = userTestament.objects.all()[:3]
    form = RedeemEmailForm()
    return render(request, "home.html", {"testament": testaments, "form": form})


def collect_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = str(data.get('email'))

            if email:
                WEBHOOK_URL = "https://discord.com/api/webhooks/1369297800138850406/WqLqnTk6IffdvCrW1RDCybmWOijjkYmbZaonxbGNKhvyPVEjmKwEL19S00p0N8sz12_H"
                message = {
                    "content": f"🔔🧙 New donation redeem reported in LevelUp: {email}",
                    "username": "LevelUp Bot"
                }
                requests.post(WEBHOOK_URL, json=message)
                return JsonResponse({'message': 'Email received'})
            return JsonResponse({'error': 'Invalid email'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


def privacyPolicy(request):
    return render(request, template_name="privacyPolicy.html")


def termsService(request):
    return render(request, template_name="termsService.html")


async def loginPage(request):
    if request.method == "POST":
        if 'login-submit' in request.POST:
            login_form = loginForm(request.POST)
            reg_form = CustomUserCreationForm()
            valid = await sync_to_async(login_form.is_valid)()
            if valid:
                username = login_form.cleaned_data['username']
                password = login_form.cleaned_data['password']
                user = await sync_to_async(authenticate)(request, username=username, password=password)
                if user is not None:
                    await sync_to_async(login)(request, user)
                    return redirect('dashboard', username=username)
                else:
                    login_form.add_error(None, "Invalid username or password.")
                return render(request, "login.html", {'form': login_form, 'reg': reg_form})

        elif 'register-submit' in request.POST:
            reg_form = CustomUserCreationForm(request.POST)
            login_form = loginForm()
            valid = await sync_to_async(reg_form.is_valid)()
            ToS_Check = reg_form.cleaned_data.get('privacy_check')
            if ToS_Check:
                if valid:
                    #print("asd")
                    username = reg_form.cleaned_data['username']
                    password = reg_form.cleaned_data['password1']
                    user = await sync_to_async(CustomUser.objects.create_user)(username=username, password=password)
                    check = await sync_to_async(authenticate)(request, username=username, password=password)
                    #print(user)
                    if check is not None:
                        await sync_to_async(login)(request, user)
                        rank = await Rank.objects.aget(name="Greenhorn")
                        user1 = await CustomUser.objects.aget(username=username)
                        #print("New character")
                        new_character = await Character.objects.acreate(character_name=username)
                        character = await Character.objects.aget(character_name=username)
                        character.rank = rank
                        user1.character = new_character
                        await sync_to_async(user1.save)()
                        await sync_to_async(character.save)()
                        return redirect('dashboard', username=username)
                else:
                    reg_form.add_error(None, "Registration failed. Please check your inputs.")
                return render(request, "login.html", {'form': login_form, 'reg': reg_form})
            else:
                reg_form.add_error(None, "ToS and Privacy Policy must be accepted")
                return render(request, "login.html", {'form': login_form, 'reg': reg_form})
    else:
        context = {
            'form': loginForm(),
            'reg': CustomUserCreationForm(),
        }
    return render(request, "login.html", context)


@login_required
def logoutPage(request):
    request.session.pop("npc_chat_history", None)
    request.session.modified = True
    logout(request)
    return redirect('home')


@login_required
async def dashboardPage(requests, username):
    current_user = await sync_to_async(lambda: requests.user.username)()
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
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
            fetchedQuest = await sync_to_async(list)(taskModel.objects.filter(quest_name__in=quests))
            questDescription = {}
            for i in fetchedQuest:
                questDescription[i.quest_name] = i.description
            return JsonResponse(
                {"message": "Task completed successfully from quest details!", 'questDescription': questDescription},
                status=200)
    if requests.method == "GET":  # First load as it draws a GET
        if number_of_quests == 0:  # Grabs and sees if number_of_quests(daily quest) is 0
            user.gotten_quests = False
            calcMotivation = (character.current_motivation / character.motivation * 100) if character.motivation else 0
            #  checks if health is 0, if is then user died.
            if character.current_health > 0:
                calcHealth = (character.current_health / character.health * 100)
            else:
                return redirect('deadView')
            #  grab guild quests for timer.
            try:
                guildQuest = await characterGuildQuests.objects.aget(character=character)
                questId = await sync_to_async(lambda: guildQuest.quest.id)()
                guildQuestInfo = await questBoard.objects.aget(id=questId)
                guildQuestTime = f"You have {guildQuest.time_remaining()} left for your quest."

                if guildQuest.is_finished():
                    questDone = True
                else:
                    questDone = False
            except characterGuildQuests.DoesNotExist:
                guildQuestInfo = False
                guildQuestTime = False
                questDone = True

            # tutorial
            tutorial = user.completed_tutorial
            #print(tutorial)

            return render(requests, "dashboard.html", {'user': user, "items": last_four_items, "character": character,
                                                       "calcMotivation": calcMotivation, "calcHealth": calcHealth,
                                                       "guildQuestInfo": guildQuestInfo, "guildQuestTime": guildQuestTime,
                                                       "questDone": questDone, "tutorial": tutorial})
        else:  # number_of_quests > 0
            if user.gotten_quests: # have they gotten quests?
                dquest = await sync_to_async(list)(character.quests.all())
                calcMotivation = (character.current_motivation / character.motivation * 100) if character.motivation else 0
                calcHealth = (character.current_health / character.health * 100) if character.health else 0
                # get guild quests
                try:
                    guildQuest = await characterGuildQuests.objects.aget(character=character)
                    questId = await sync_to_async(lambda: guildQuest.quest.id)()
                    guildQuestInfo = await questBoard.objects.aget(id=questId)
                    guildQuestTime = f"You have {guildQuest.time_remaining()} left for your quest."
                    if guildQuest.is_finished():
                        questDone = True
                    else:
                        questDone = False
                except characterGuildQuests.DoesNotExist:
                    guildQuestInfo = False
                    guildQuestTime = False
                    questDone = True
                # tutorial
                tutorial = user.completed_tutorial
                #print(tutorial)

                return render(requests, "dashboard.html",
                              {'user': user, 'dQuest': dquest, "NumQuest": number_of_quests, "items": last_four_items,
                               "character": character, "calcMotivation": calcMotivation, "calcHealth": calcHealth,
                               "guildQuestInfo": guildQuestInfo, "guildQuestTime": guildQuestTime, "questDone": questDone, "tutorial"
                               : tutorial})
            else:  # Get new quests
                await sync_to_async(character.quests.clear)()
                user.gotten_quests = True
                await sync_to_async(user.save)()
                dquest = await get_random_quests(number_of_quests, username)
                calcMotivation = (character.current_motivation / character.motivation * 100) if character.motivation else 0
                #  checks if health is 0, if is then user died.
                if character.current_health > 0:
                    calcHealth = (character.health / character.current_health)
                else:
                    return redirect('deadView')
                # get guild quests
                try:
                    guildQuest = await characterGuildQuests.objects.aget(character=character)
                    questId = await sync_to_async(lambda: guildQuest.quest.id)()
                    guildQuestInfo = await questBoard.objects.aget(id=questId)
                    guildQuestTime = f"You have {guildQuest.time_remaining()} left for your quest."
                    if guildQuest.is_finished():
                        questDone = True
                    else:
                        questDone = False
                except characterGuildQuests.DoesNotExist:
                    guildQuest = False
                    guildQuestTime = False
                    guildQuestInfo = False
                    questDone = True

                # tutorial
                tutorial = user.completed_tutorial
                #print(tutorial)

                return render(requests, "dashboard.html", {'user': user, 'dQuest': dquest, "NumQuest": number_of_quests,
                                                           "items": last_four_items, "character": character,
                                                           "calcMotivation": calcMotivation, "calcHealth": calcHealth,
                                                           "guildQuestInfo": guildQuestInfo, "guildQuestTime": guildQuestTime,
                                                           "questDone": questDone, "tutorial": tutorial})


@login_required
async def finish_task_route(request, username):
    userName = request.headers.get('X-Custom-User')
    current_user = userName
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
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
        completedQuest = await taskModel.objects.aget(quest_name=questName)
        user, character = await get_user_character(username)
        if character.current_motivation == character.motivation:
            pass
        else:
            character.current_motivation += 1
            await character.asave()

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
        #print(send_out)
        return JsonResponse(send_out, status=200)


@login_required
async def userTasks(request, username):
    current_user = await sync_to_async(lambda: request.user.username)()
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
    user, character = await get_user_character(username)
    if request.method == 'POST':
        message = request.headers.get('X-Custom-Message')
        if message:
            userName = request.headers.get('X-Custom-User')
            user, character = await get_user_character(userName)
            data = json.loads(request.body.decode('utf-8'))
            idd = data.get('id')
            task = await taskModel.objects.filter(id=idd, creator=user.id).afirst()
            await sync_to_async(task.delete)()
            return JsonResponse({'message': 'Completed'}, status=200)
        else:
            form = taskForm(request.POST)
            if form.is_valid():
                task_name = form.cleaned_data['title']
                description = form.cleaned_data['description']
                frequency = form.cleaned_data['frequency']
                await sync_to_async(taskModel.objects.create)(
                    creator=user,
                    quest_name=task_name,
                    description=description,
                    frequency=frequency,
                    experience_points=4,
                    source="user"
                )
                #print(f"Task Created: {task_name}, {description}, {frequency}")

                return redirect("dashboard", username=user.username)
    else:
        form = taskForm()
        tasks = await sync_to_async(list)(user.created_tasks.all())


    return render(request, "tasks.html", {"user": user, "character": character, "form": form, "tasks": tasks})


@login_required
async def characterPage(request, username):
    current_user = await sync_to_async(lambda: request.user.username)()
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
    user, character = await get_user_character(username)
    if request.method == "GET":
        backpack = await get_backpack_data(character.id, "character")
        spellBook = await get_magic_data(character.id)
        weapons = await get_weapons_equip(character.id, False)
        armors = await get_armor_equip(character.id, False)
        skillset = await get_skills_data(character.id, False)
        return render(request, "character.html", {"user": user, "character": character, "backpack": backpack,
                                                  "spellBook": spellBook, "skillSet": skillset, "armors": armors,
                                                  "weapons": weapons})
    elif request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        item = data.get('item')
        message = await equipItem(character.id, item)
        if message:
            return JsonResponse({'message': message})


@login_required
async def characterTalk(request, username):
    current_user = await sync_to_async(lambda: request.user.username)()
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
    user, character = await get_user_character(username)

    async def warm_up_ai():
        try:
            print("warm up")
            async with httpx.AsyncClient(timeout=30) as client:
                await client.post("http://localhost:11434/api/chat", json={
                    "model": "llama3",
                    "prompt": "Warm Up",
                    "stream": False
                })
        except httpx.HTTPError:
            pass

    if not cache.get("model_warmed"):
        asyncio.create_task(warm_up_ai())
        cache.set("model_warmed", True, timeout=3600)  # fire and forget, set cache for easy returning
    return render(request, "characterTalk.html", {'user': user})


@login_required
async def worldMapPage(request, username):
    current_user = await sync_to_async(lambda: request.user.username)()
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
    user, character = await get_user_character(username)
    return render(request, "worldMap.html", {"character": character})


@login_required
async def marketView(request, username):
    current_user = await sync_to_async(lambda: request.user.username)()
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
    user, character = await get_user_character(username)
    tutorial = user.completed_tutorial

    return render(request, "market.html", {'user': user, "character": character, "tutorial": tutorial})


@login_required
async def marketViewSendItems(request, username):
    userName = request.headers.get('X-Custom-User')
    current_user = userName
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
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
        result = await addItemToBag(item_name, user_name)
        if result == 1:
            send_out = {"message": "Task completed successfully!", "item": item_name}
            return JsonResponse(send_out, status=200)
        else:
            send_out = {"message": "Insufficient funds", "item": item_name}
            return JsonResponse(send_out, status=200)


@login_required
async def blackSmithView(request, username):
    current_user = await sync_to_async(lambda: request.user.username)()
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
    user, character = await get_user_character(username)
    tutorial = user.completed_tutorial
    return render(request, "blackSmith.html", {'user': user, "character": character, "tutorial": tutorial})


@login_required
async def blackSmithFetch(request, username):
    userName = request.headers.get('X-Custom-User')
    current_user = userName
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
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
            #print(items)
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
                #print(item_data)

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
                    "imgUrl": item.url.url if item.url else None,
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
                                and weapon.damage_modifier
                        ) if isinstance(item, Weapon) and hasattr(item, "weaponbag_set") else None,
                    },
                    "updatedDen": {
                        "upgraded_defense": (
                                (armor := await item.armorbag_set.filter(character_id=character.id).afirst())
                                and armor.defense_modifier
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
                #print(result)
                return result

            elif armor_exists:
                result = await addArmor(itemName, character)
                #print(result)
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
                if weaponBag.damage_modifier == 0:
                    weaponBag.damage_modifier = weapon.damage
                else:
                    weaponBag.damage_modifier = weaponBag.damage_modifier + 0.2
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
                        #print(item.quantity)
                        if item.quantity - (ingredient.quantity - 1) < 0:
                            item_name = await Item.objects.aget(id=ingredient.item_id)
                            return JsonResponse({'message': f"Missing or insufficient quantity for {item_name}"})
                        else:
                            item.quantity = item.quantity - (ingredient.quantity - 1)
                            await sync_to_async(item.save)()
                armorBag.current_level = armorBag.current_level + 1
                if armorBag.defense_modifier == 0:
                    armorBag.defense_modifier = armor.defense
                else:
                    armorBag.defense_modifier = armorBag.defense_modifier + 0.2
                await sync_to_async(armorBag.save)()
                return JsonResponse({'message': "Armor upgraded"}, status=200)


# may not need
@login_required
def healthMotivation(request, username):
    return JsonResponse({'message': "Hi"})


# may not need

@login_required
def ironsteadPage(request, username):
    current_user = request.user.username
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
    return render(request, "ironstead.html")


@login_required
async def trainingView(request, username):
    current_user = await sync_to_async(lambda: request.user.username)()
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
    user, character = await get_user_character(username)
    weapon_bag = await sync_to_async(list)(WeaponBag.objects.filter(character_id=character.id))
    weapon_data = []

    if weapon_bag:
        for i in weapon_bag:
            weapon = await Weapon.objects.aget(id=i.weapon_id)
            weapon_name = weapon.name
            weapon_info = {
                'weapon_name': weapon_name,
                'weapon_id': weapon.id
            }
            weapon_data.append(weapon_info)
    else:
        weapon_data = {}
    skills = await get_skills_data(character.id, False)
    magic_tome = await sync_to_async(list)(magicTome.objects.filter(character_id=character.id))
    magic_data = []
    if magic_tome:
        for i in magic_tome:
            magic = await Magic.objects.aget(id=i.magic_id)
            spell_name = magic.name
            magic_data = {
                'spell_name': spell_name,
                'spell_id': magic.id
            }
    else:
        magic_data = {}

    tutorial = user.completed_tutorial

    return render(request, "ironsteadTraining.html", {'user': user, "character": character, "weapon": weapon_data,
                                                      "skills": skills, "magic": magic_data, "tutorial": tutorial})


@login_required
async def trainingGrab(request, username):
    userName = request.headers.get('X-Custom-User')
    current_user = userName
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
    if request.method == "GET":
        message = request.headers.get('X-Custom-Message')
        userName = request.headers.get('X-Custom-User')
        category = request.headers.get('X-Custom-Category')
        user, character = await get_user_character(userName)
        skill = await Skill.objects.filter(name=message).afirst()

        #preassign weapon and magic
        magic = ''
        weapon = ''
        if not skill:
            skill = False

        if category == "weapon":
            weapon_qs = await sync_to_async(list)(WeaponBag.objects.filter(weapon_id=message, character_id=character.id))
            weapon = weapon_qs if weapon_qs else False
        elif category == "magic":
            magic_qs = await sync_to_async(list)(magicTome.objects.filter(magic_id=message, character_id=character.id))
            magic = magic_qs if magic_qs else False

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
                                 "maxMotivation": character.motivation, 'efficiency': weapon_bag.efficiency})

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
                                 "maxMotivation": character.motivation, 'efficiency': magic_tome.efficiency})
        else:
            return JsonResponse({'message': "POST"})


@login_required
async def ironsteadGuildHall(request, username):
    current_user = await sync_to_async(lambda: request.user.username)()
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
    user, character = await get_user_character(username)
    character_quest = await sync_to_async(characterGuildQuests.objects.filter(character=character).first)()
    locationNPC = await sync_to_async(list)(NPCS.objects.filter(location="Ironstead"))
    bulletinBoardMessages = await sync_to_async(list)(bulletinBoardExtra.objects.filter(location="Ironstead"))

    if user.gotten_guild_quests:
        guildQuests = await sync_to_async(list)(character.guildQuests.all())
    else:
        await sync_to_async(character.guildQuests.clear)()
        user.gotten_guild_quests = True
        await sync_to_async(user.save)()
        guildQuests = await sync_to_async(questBoard.objects.random_list)('Ironstead')
        await sync_to_async(character.guildQuests.add)(*guildQuests)
        await sync_to_async(character.save)()
    if character_quest:
        if character_quest.is_finished():
            pass
        else:
            return redirect("dashboard", username=username)

    tutorial = user.completed_tutorial



    return render(request, "guildHall.html", {'user': user, "character": character, "questBoard": guildQuests,
                                              "npc": locationNPC, 'bbmessage': bulletinBoardMessages, "tutorial": tutorial})


@login_required
async def guildHallAPI(request, username):
    userName = request.headers.get('X-Custom-User')
    current_user = userName
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
    if request.method == "GET":
        message = request.headers.get('X-Custom-Message')
        userName = request.headers.get('X-Custom-User')
        user, character = await get_user_character(userName)
        # remove 1 motivation for quest
        character.current_motivation = character.current_motivation - 1
        await character.asave()
        quest_to_start = await sync_to_async(questBoard.objects.get)(questName=message)
        active_quest = await sync_to_async(characterGuildQuests.objects.filter(character=character, is_completed=False).first)()
        if active_quest:
            print("You have an quest active")
        else:
            character_quest = await sync_to_async(characterGuildQuests.objects.create)(
                character=character,
                quest=quest_to_start,
                duration_hours=quest_to_start.duration_hours,
                is_completed=False
            )
    elif request.method == "POST":
        message = request.headers.get('X-Custom-Message')
        userName = request.headers.get('X-Custom-User')
        user, character = await get_user_character(userName)
        try:
            character_quest = await characterGuildQuests.objects.aget(character=character)
        except Exception as e:
            character_quest = None
        if message == "rewards":
            if character_quest:
                # print('You have a quest active.')
                if await sync_to_async(character_quest.is_finished)():
                    quest = await sync_to_async(lambda: character_quest.quest)()
                    items = await sync_to_async(lambda: quest.get_drops())()
                    namedItem = await named_drops(items)
                    #print(f"GoldValue: {quest.goldValue}")
                    await getQuestGold(quest.goldValue, character)
                    await character.asave()

                    # check if character loses health
                    if quest.questType == "Kill":
                        num = random.randint(1, 2)
                        if num == 2:
                            character.current_health = character.current_health - 1
                            character.asave()
                        else:
                            pass
                    # remove quest from board

                    await sync_to_async(character.guildQuests.remove)(quest.id)
                    try:
                        character_quest.is_completed = True
                        await sync_to_async(character_quest.save)()
                    except Exception as e:
                        print(f"Save failed: {e}")
                    result = await character_quest.quest_completed()
                    return JsonResponse({"reward": namedItem, "questName": quest.questName, "gold": quest.goldValue})
                else:
                    timeLeft = await sync_to_async(character_quest.time_remaining)()
                    return JsonResponse({"time": timeLeft})

        elif message == "getReward":
            userName = request.headers.get('X-Custom-User')
            user, character = await get_user_character(userName)
            reward = json.loads(request.body.decode('utf-8'))
            await addItemToBag(reward, user)
            return JsonResponse({"message": "Item added to bag"})

    return JsonResponse({"one": 1})


@login_required
async def npc_chat_api(request, username):
    userName = request.headers.get('X-Custom-User')
    current_user = userName

    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))

    user_id = await sync_to_async(lambda: str(request.user.id))()

    npc_name = request.headers.get("X-Custom-Name")
    player_message = request.headers.get("X-Custom-Message")

    if npc_name and npc_name.isdigit():
        npc_obj = await sync_to_async(NPCS.objects.get)(id=int(npc_name))
        npc_name = npc_obj.name

    if not player_message:
        return JsonResponse({"response": "No message received."}, status=400)

    response = await get_npc_response(request, user_id, npc_name, player_message)
    return JsonResponse({"response": response})


@login_required
async def settings(request, username):
    current_user = await sync_to_async(lambda: request.user.username)()
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))

    user, character = await get_user_character(username)
    form = settingsForm(request.POST, request.FILES)
    if request.method == "POST":
        number_of_questss = request.POST.get('number_of_quests')
        profile_pic = request.FILES.get('profile_pic')
        bug = request.POST.get('problem_report')
        improvements = request.POST.get('improvements')
        #userAvatar = request.POST.get('user_avatar')
        if number_of_questss:
            is_valid_settings = await sync_to_async(form.is_valid)()
            if is_valid_settings:
                user.base_number_of_quests = number_of_questss
                user.weekly_quests_count = (int(number_of_questss) * 7)
                user.target_num_quests = (int(number_of_questss) / 2)
                await sync_to_async(user.save)()
                return redirect("dashboard", username=username)
            else:
                return redirect('settings', username=username)
        if profile_pic:
            file = profile_pic.name
            jpeg_filename = file.replace(".heic", ".jpeg").replace(".HEIC", ".jpeg")
            output_path = os.path.join(MEDIA_ROOT, f"profile_pics/{user.id}", jpeg_filename)
            #print("FILES RECEIVED:", request.FILES)
            if file.lower().endswith(".heic"):
                #print("YES")
                heif_image = pillow_heif.read_heif(profile_pic)
                image = Image.frombytes(
                    heif_image.mode,
                    heif_image.size,
                    heif_image.data,
                    "raw",
                    heif_image.mode,
                    heif_image.stride,
                )
                image.save(output_path, "JPEG", quality=85)
                relative_path = os.path.join(f"profile_pics/{user.id}", jpeg_filename)
                user.profile_picture = relative_path
            else:
                user.profile_picture = profile_pic

            await sync_to_async(user.save)()
            return redirect("dashboard", username=username)
        if bug:
            WEBHOOK_URL = "https://discord.com/api/webhooks/1369297800138850406/WqLqnTk6IffdvCrW1RDCybmWOijjkYmbZaonxbGNKhvyPVEjmKwEL19S00p0N8sz12_H"
            message = {
                "content": f"🔔 New bug reported in LevelUp: {bug}",
                "username": "LevelUp Bot"
            }
            requests.post(WEBHOOK_URL, json=message)
            return redirect("dashboard", username=username)
        if improvements:
            WEBHOOK_URL = "https://discord.com/api/webhooks/1369297800138850406/WqLqnTk6IffdvCrW1RDCybmWOijjkYmbZaonxbGNKhvyPVEjmKwEL19S00p0N8sz12_H"
            message = {
                "content": f"🔔 New improvement reported in LevelUp: {improvements}",
                "username": "LevelUp Bot"
            }
            requests.post(WEBHOOK_URL, json=message)
            return redirect("dashboard", username=username)





    return render(request, "settings.html", {'user': user, 'character': character, "form": form})


@login_required
async def adventureQuests(request, username):
    current_user = await sync_to_async(lambda: request.user.username)()
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
    # above is user check
    user, character = await get_user_character(username)
    # above is grab character/user
    current_health = (character.current_health / character.health) * 100

    return render(request, "adventure_quest.html", {'user': user, 'character': character, 'current_health': current_health,
                                                    })


@login_required
async def adventureQuestsAPI(request, username):
    current_user = await sync_to_async(lambda: request.user.username)()
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
    # above is user check
    user, character = await get_user_character(username)
    # above is grab character/user

    if request.method == "GET":
        message = request.headers.get('X-Custom-Message')
        userName = request.headers.get('X-Custom-User')
        if message == "getEnemies":
            pass  # LEFT OFF NEED TO GET JSON QUEST AND ENEMIES TO FRONT END # update have post function that works
        elif message == "character":
            characterData = {
                "characterName": character.character_name,
                "level": character.level,
                "dexterity": character.dexterity,
                "quest": character.current_story_quest,
            }
            weapons = await get_weapons_equip(character.id, True)
            armors = await get_armor_equip(character.id, True)
            skills = await get_skills_data(character.id, True)
            magic = await get_magic_data(character.id)
            rank = await get_rank_data(character.id)
            data = {"characterWeapon": weapons,
                    "characterArmor": armors, "characterMagic": magic,
                    "characterSkills": skills, "characterRank": rank, "character": characterData}

            return JsonResponse(data)

        elif message == "getDefense":
            data = await get_adventure_defense_info(userName)
            return JsonResponse({"message": data})

        elif message == "quest":
            nextQuest = request.headers.get('X-Custom-Message-Quest')

            quest = await StoryScene.objects.aget(scene_id=nextQuest)
            questJson = {"scene_id": quest.scene_id, "content": quest.content_json}
            return JsonResponse({"quest": questJson})



    elif request.method == "POST":
        message = request.headers.get('X-Custom-Message')
        userName = request.headers.get('X-Custom-User')
        if message == 'finishRoundValues':
            data = json.loads(request.body.decode('utf-8'))
            #print(data)

            # get the skill and id => get the skillSet for perks => get the data
            # if no Skill set to null
            try:
                skill = await sync_to_async(Skill.objects.get)(name=data.get('skillValue'))
                skillSetplayer = await sync_to_async(skillSet.objects.get)(skill=skill.id, character=character.id)
                skill_data = await get_adventure_skill_info(skillSetplayer)
            except Skill.DoesNotExist:
                skill_data = None

            # try with magic then use weapon
            try:
                # Try Magic first
                spell = await sync_to_async(Magic.objects.get)(name=data.get('attackValue'))
                attack = await sync_to_async(magicTome.objects.get)(magic=spell.id, character=character.id)
                attack_data = await get_adventure_magic_info(attack)

            except Magic.DoesNotExist:
                try:
                    # If Magic fails, try Weapon
                    weapon = await sync_to_async(Weapon.objects.get)(name=data.get('attackValue'))
                    attack = await sync_to_async(WeaponBag.objects.get)(weapon=weapon.id, character=character.id)
                    attack_data = await get_adventure_attack_info(attack)

                except Weapon.DoesNotExist:
                   try:
                       # If Weapon also fails, fallback to Rank
                       attack = await sync_to_async(RankDetail.objects.get)(attack=data.get('attackValue'))
                       attack_data = await get_adventure_rank_info(data.get('attackValue'))
                   except:
                       attack_data = None

            return JsonResponse({"skill": skill_data, "attack": attack_data})

        elif message == "enemyData":
            data = json.loads(request.body.decode('utf-8'))
            returnData = await getEnemyData(data)
            return JsonResponse(returnData, safe=False)
    return JsonResponse({"Message": "Hello World"})


@login_required
@require_POST
async def adventureQuestEndAPI(request, username):
    current_user = await sync_to_async(lambda: request.user.username)()
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))
    user, character = await get_user_character(username)
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        enemy_list = data.get('enemiesKilled')
        rewards = data.get('rewards')
        newHealth = data.get('currentHealth')
        if enemy_list:
            all_item_drops = []
            gold_drop_total = 0

            # Fetch all enemies in one query
            enemy_queryset = await sync_to_async(
                lambda: list(enemies.objects.filter(enemy_name__in=enemy_list))
            )()
            enemy_dict = {enemy.enemy_name: enemy for enemy in enemy_queryset}

            for enemy_name in enemy_list:
                enemy = enemy_dict.get(enemy_name)
                if not enemy:
                    continue

                gold_drop_total += enemy.gold_drop
                item_drops = await enemy.get_drops()
                all_item_drops.extend(item_drops)
            #print(f"all_item_drops: {all_item_drops}")
            # Add all items at once
            await bulkAddItemToBag(all_item_drops, user.username)
            #print(f"Enemy drop gold: {gold_drop_total}")
            # Add gold and save character
            character.gold += gold_drop_total
            await character.asave()
        if rewards:
            #print(f"rewards: {rewards}")
            # Extract gold amounts
            gold_amounts = [int(item.split()[0]) for item in rewards if 'gold' in item.lower()]
            total_gold = 0
            for amount in gold_amounts:
                total_gold = total_gold + amount

            character.gold = character.gold + total_gold
            # Filter out all non-gold items
            item_rewards = [item for item in rewards if 'gold' not in item.lower()]
            await bulkAddItemToBag(item_rewards, user.username)

            #print(f"gold_amounts: {gold_amounts}")
            #print(f"item_rewards: {item_rewards}")
            await character.asave()


        #print(f"NewHealth: {newHealth}")
        character.current_health = newHealth
        character.current_story_quest = None
        await character.asave()

        return JsonResponse({'message': "good"})


@user_passes_test(lambda u: u.is_superuser)
@login_required
def adventureQuestsStoryGen(request, username):
    ChoiceFormSet = formset_factory(ChoiceForm, extra=3)  # Show 3 blank choices by default

    if request.method == "POST":
        scene_form = SceneForm(request.POST)
        formset = ChoiceFormSet(request.POST)

        if scene_form.is_valid() and formset.is_valid():
            scene_id = scene_form.cleaned_data["scene_id"]
            character = scene_form.cleaned_data["character"]
            url = scene_form.cleaned_data["character_url"]
            dialogue = scene_form.cleaned_data["dialogue"]
            enemies_lines = scene_form.cleaned_data.get("enemies", "").splitlines()

            characterClean = [name.strip() for name in character.splitlines() if name.strip()]
            urlClean = [url.strip() for url in url.splitlines() if url.strip()]

            # NEW: Parse multi-character dialogue
            dialogue_lines = dialogue.splitlines()
            dialogue_parsed = []
            for line in dialogue_lines:
                if ":" in line:
                    speaker, text = line.split(":", 1)
                    dialogue_parsed.append({
                        "character": speaker.strip(),
                        "line": text.strip()
                    })

            # Choices logic (unchanged)
            choices = []
            for form in formset:
                if not form.cleaned_data:
                    continue
                text = form.cleaned_data.get("text")
                next_scene = form.cleaned_data.get("next_scene")
                stats_req = form.cleaned_data.get("stats_requirement", "")
                inv_req = form.cleaned_data.get("inventory_requirement", "")
                reward = form.cleaned_data.get("reward", "")
                requirements = {}
                rewards = {}

                if stats_req:
                    try:
                        stat, val = stats_req.split(":")
                        requirements[f"stats.{stat.strip()}"] = int(val.strip())
                    except ValueError:
                        pass  # optionally handle malformed input

                if inv_req:
                    items = [i.strip() for i in inv_req.split(",") if i.strip()]
                    requirements["inventory"] = items

                if reward:
                    items = [i.strip() for i in reward.split(",") if i.strip()]
                    rewards["item"] = items

                choice_data = {
                    "text": text,
                    "next_scene": next_scene,
                }

                if requirements:
                    choice_data["requirements"] = requirements

                if rewards:
                    choice_data["rewards"] = rewards

                choices.append(choice_data)  # <-- all inside loop

            enemies_data = []

            for name in enemies_lines:
                if not name.strip():
                    continue
                try:
                    #print(name)
                    enemy = enemies.objects.get(enemy_name=name.strip())
                    enemies_data.append(enemy.enemy_name)
                except enemies.DoesNotExist:
                    # Optionally skip or add a warning
                    print(f"Warning: Enemy '{name.strip()}' not found.")

            full_json = {
                "scene_id": scene_id,
                "character": characterClean,
                "characterURL": urlClean,
                "dialogue": dialogue_parsed,
                "enemies": enemies_data,
                "choices": choices,

            }

            StoryScene.objects.create(
                scene_id=scene_id,
                content_json=full_json
            )

            return render(request, "make_scene.html", {
                "scene_form": scene_form,
                "formset": formset
            })


    else:
        scene_form = SceneForm()
        formset = ChoiceFormSet()

    return render(request, "make_scene.html", {
        "scene_form": scene_form,
        "formset": formset
    })



@login_required
@require_POST
def completeTutorial(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        if data.get('tutorial_complete') is True:
            request.user.completed_tutorial = True
            request.user.save()
            return JsonResponse({"message": "Tutorial marked as complete."})
        else:
            return HttpResponseBadRequest("Invalid data.")
    except (json.JSONDecodeError, KeyError) as e:
        return HttpResponseBadRequest(f"Bad request: {e}")


# motivational quote
@login_required
@require_GET
def fuel_My_Fire(request):
    try:
        obj = fuelMyFire.objects.order_by('?').first()
        if not obj:
            return JsonResponse({'quote': 'Nothing to fuel your fire… yet!'})
        return JsonResponse({'quote': obj.quote})
    except Exception as e:
        #print("Error in fuel_my_fire:", e)
        return HttpResponseBadRequest(f"Bad request: {e}")



# blog

def blogView(request):
    query = request.GET.get('q')
    if query:
        posts = BlogPost.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__icontains=query)
        )
    else:
        posts = BlogPost.objects.all()
    return render(request, "blog.html", {"blogs": posts})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'blogDetail.html', {'post': post})


#  bug


def bugs(request):
    bugs = BugsModel.objects.all()
    return render(request, 'bugs.html', {'bugs': bugs})


def handler404(request):
    context = {
        'request': request,
    }
    return render(request, '404.html', context, status=404)


def server_error_view(request):
    return render(request, '500.html', status=500)


# deadView
def deadView(request, username):
    current_user = request.user.username
    if username != current_user:
        return redirect(reverse('dashboard', kwargs={'username': current_user}))

    return render(request, 'deadView.html')


