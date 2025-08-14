from celery import shared_task
from django.db import connection, close_old_connections
from django.db.models import F


@shared_task
def reset_quests_task():
    # Prevent stale DB connection
    close_old_connections()

    from core.models import CustomUser, Character

    # Reset all users' quest counters in one query
    CustomUser.objects.update(
        number_of_quests=F('base_number_of_quests'),
        target_num_quests_inc=0,
        gotten_quests=False,
        gotten_guild_quests=False
    )

    # Reset all characters' motivation
    Character.objects.update(
        current_motivation=F('motivation')
    )

    print("Quests reset successfully.")
