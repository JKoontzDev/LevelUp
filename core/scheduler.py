from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime
from django.db.models import F
from django.db import connection


def reset_quests_at_midnight():
    from core.models import CustomUser, Character
    if not connection.is_usable():
        print("Database connection not usable.")
        return
    CustomUser.objects.all().update(number_of_quests=F('base_number_of_quests'))
    CustomUser.objects.all().update(target_num_quests_inc=0)
    CustomUser.objects.all().update(gotten_quests=False)
    CustomUser.objects.all().update(gotten_guild_quests=False)
    Character.objects.all().update(current_motivation=F('motivation'))

    print("Quests reset successfully.")
    print("Testing")


def start_scheduler():
    jobstores = {
        'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')  # Persist jobs across restarts
    }
    scheduler = BackgroundScheduler(jobstores=jobstores)
    scheduler.add_job(
        reset_quests_at_midnight,
        'cron',
        hour=0,
        minute=0,
        misfire_grace_time=3600  # Allow a grace period of 1 hour for missed runs
    )
    scheduler.start()
    print("Scheduler started.")
