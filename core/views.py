from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from core.models import *
from django.http import JsonResponse
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
        #print("Week compelte")
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




#routes

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
    return render(request, "login.html", {'form': form, 'reg': RegForm,  'errors': RegForm.errors})


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
            #print(f"change_noq is {NumberQuests}")
            user.number_of_quests = NumberQuests
            quest_to_remove = character.quests.filter(id=questID)
            character.quests.remove(*quest_to_remove)
            user.save()
            character.save()
            new_num_quests = user.number_of_quests
            return JsonResponse({"message": "Task completed successfully from dashboard!", "newNumQuest": new_num_quests}, status=200)
        elif message == 'Get quest details!':  # gets quest details from frontend
            data = json.loads(requests.body.decode('utf-8'))
            quests = data.get('quests')
            fetchedQuest = dailyQuest.objects.filter(quest_name__in=quests)
            questDescription = {}
            for i in fetchedQuest:
                questDescription[i.quest_name] = i.quest_description
            return JsonResponse({"message": "Task completed successfully from quest details!", 'questDescription': questDescription}, status=200)
    if requests.method == "GET":
        if number_of_quests == 0:
            user.gotten_quests = False
            return render(requests, "dashboard.html", {'user': user, "items": last_four_items, "character": character})
        else:
            if user.gotten_quests:
                dquest = character.quests.all()
                return render(requests, "dashboard.html",
                              {'user': user, 'dQuest': dquest, "NumQuest": number_of_quests, "items": last_four_items,
                               "character": character})
            else:
                character.quests.clear()
                user.gotten_quests = True
                user.save()
                dquest = get_random_quests(number_of_quests, username)
                return render(requests, "dashboard.html", {'user': user, 'dQuest': dquest, "NumQuest": number_of_quests,
                                                           "items": last_four_items, "character": character})


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
    return render(request, "character.html")


@login_required
def mapPage(request, username):
    return render(request, "map.html")


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
        return JsonResponse(itemsToPage, status=200, safe=False,)

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
