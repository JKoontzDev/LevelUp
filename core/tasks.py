from celery import shared_task
from django.db import connection
from django.db.models import F
from core.models import CustomUser, Character


@shared_task
def reset_quests_task():
    if not connection.is_usable():
        print("Database connection not usable.")
        return
    CustomUser.objects.all().update(number_of_quests=F('base_number_of_quests'))
    CustomUser.objects.all().update(target_num_quests_inc=0)
    CustomUser.objects.all().update(gotten_quests=False)
    CustomUser.objects.all().update(gotten_guild_quests=False)
    Character.objects.all().update(current_motivation=F('motivation'))

    print("Quests reset successfully.")
