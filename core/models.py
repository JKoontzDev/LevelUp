from django.contrib.auth.models import AbstractUser
from django.db import models
import random


class Rank(models.Model):
    name = models.CharField(max_length=100)
    min_level = models.IntegerField()
    max_level = models.IntegerField()

    def __str__(self):
        return self.name


class RankDetail(models.Model):
    description = models.CharField(max_length=200)
    special_attack = models.CharField(max_length=50)
    special_attack_damage = models.IntegerField()
    rank = models.OneToOneField(Rank, on_delete=models.SET_NULL, related_name='details', null=True,
                                blank=True)  # One-to-one relation with Rank

    def __str__(self):
        return f"Details for {self.rank.name}"



class DropClass(models.TextChoices):
    COMMON = 'common', 'Common'
    UNCOMMON = 'uncommon', 'Uncommon'
    RARE = 'rare', 'Rare'
    EPIC = 'epic', 'Epic'
    LEGENDARY = 'legendary', 'Legendary'


class typeClass(models.TextChoices):
    INGREDIENT = 'ingredient', 'Ingredient'
    WEAPON = 'weapon', 'Weapon'
    ARMOR = 'armor', 'Armor'
    OBJECT = 'object', 'Object'


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    drop_class = models.CharField(
        max_length=20,
        choices=DropClass.choices,
        default=DropClass.COMMON
    )
    type = models.CharField(
        max_length=20,
        choices=typeClass.choices,
        default=typeClass.INGREDIENT
    )
    damage = models.IntegerField(null=True, blank=True)
    healing = models.IntegerField(null=True, blank=True)
    drop_rate = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    marketable = models.BooleanField(default=False)
    market_drop_rate = models.FloatField(default=50.0)


    def __str__(self):
        return self.name



class Skill(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    level_required = models.IntegerField()  # Example: skill level required to learn this skill
    damage = models.IntegerField(null=True, blank=True)
    healing = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class BackpackItem(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey('Item', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} (owned by {self.character.character_name})"


class Character(models.Model):
    character_name = models.CharField(max_length=50)
    skills = models.ManyToManyField(Skill, blank=True)
    backpack = models.ManyToManyField(
        Item,
        through='BackpackItem',
        related_name='backpack_items',
        blank=True
    )
    current_equip_items = models.ManyToManyField(Item, related_name='equipped_items', blank=True)
    level = models.IntegerField(default=1)  # Add your custom field
    rank = models.ForeignKey(Rank, on_delete=models.CASCADE, related_name='character', null=True,
                             blank=True)  # ForeignKey to Rank
    exp = models.IntegerField(default=0)
    gold = models.IntegerField(default=0)
    quests = models.ManyToManyField('dailyQuest', related_name='characters')

    def __str__(self):
        return self.character_name

    def delete(self, *args, **kwargs):
        self.backpack.through.objects.filter(character=self).delete()
        self.current_equip_items.through.objects.filter(character=self).delete()

        super().delete(*args, **kwargs)


class CustomUser(AbstractUser):
    number_of_quests = models.IntegerField(default=4)  # changes as you complete quests throughout the day.
    target_num_quests = models.IntegerField(default=2)  # you can have as many quests as you want but this amount is how
    # many you need to complete the day ^
    target_num_quests_inc = models.IntegerField(default=0)  # used to check if target num quests is met
    completed_quests = models.IntegerField(default=0)  # increments up 1 when a quest is finished used for the percent_weekly_completed
    base_number_of_quests = models.IntegerField(default=4)  # set number from setting
    weekly_quests_count = models.IntegerField(default=0)  # base_number_of_quests * 7 used for percentage on dashboard
    percent_weekly_completed = models.FloatField(default=0.00)  # the percentage of completed quests per week!
    completed_days = models.IntegerField(default=0)  # used to keep track of days where you complete all tasks
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='character', null=True,
                             blank=True)
    gotten_quests = models.BooleanField(default=False)  # used to check if they have gotten new daily quests


    def __str__(self):
        return self.username

    def delete(self, *args, **kwargs):
        if self.character:
            self.character.backpack.through.objects.filter(character=self.character).delete()
            self.character.delete()
        super().delete(*args, **kwargs)


class dailyQuest(models.Model):
    quest_name = models.CharField(max_length=50)
    quest_description = models.TextField()
    experience_points = models.IntegerField()
    drop_class = models.CharField(
        max_length=20,
        choices=DropClass.choices,
        default=DropClass.COMMON
    )

    def get_drops(self):
        drops = []
        items = Item.objects.filter(drop_class=self.drop_class)
        randomized_items = items.order_by('?')
        for item in randomized_items:
            if random.uniform(0, 100) <= item.drop_rate:
                drops.append(item.id)
                break
        return drops



