from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
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
    OBJECT = 'object', 'Object'


# game items

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
    drop_rate = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    marketable = models.BooleanField(default=False)
    market_drop_rate = models.FloatField(default=50.0)
    forgeIngredient = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class equipablesIngredients(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    weapon = models.ForeignKey('Weapon', on_delete=models.CASCADE, null=True, blank=True)
    armor = models.ForeignKey('Armor', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} )"


class Weapon(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    max_durability = models.IntegerField(default=10)
    damage = models.IntegerField()
    attack_speed = models.FloatField(default=1.0)
    critical_rate = models.FloatField(default=0.0)
    forgeable = models.BooleanField(default=False)
    repair_cost = models.IntegerField(default=10)
    crafting_ingredients = models.ManyToManyField(Item, related_name='used_for_weapon', through=equipablesIngredients,
                                                  blank=True)

    def __str__(self):
        return f"Weapon: {self.name}"



class Magic(models.Model):
    name = models.CharField(max_length=40, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    level = models.IntegerField(null=True, blank=True)
    damage = models.IntegerField()
    healing = models.IntegerField()
    special = models.CharField(max_length=100, null=True, blank=True)


class Armor(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    max_durability = models.IntegerField(default=10)
    defense = models.IntegerField()
    resistance = models.IntegerField(null=True, blank=True)
    forgeable = models.BooleanField(default=False)
    repair_cost = models.IntegerField(default=10)
    crafting_ingredients = models.ManyToManyField(Item, related_name='used_for_armor', through=equipablesIngredients,
                                                  blank=True)

    def __str__(self):
        return f"Armor: {self.name}"


class skillType(models.TextChoices):
    GENERAL = 'general', 'General'
    COMBAT = 'combat', 'Combat'
    MAGIC = 'magic', 'Magic'
    UTILITY = 'utility', 'Utility'
    MOTIVATIONAL = 'motivational', 'Motivational'
    UNIQUE = 'unique', 'Unique'


class Skill(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    level_required = models.IntegerField()
    skill_type = models.CharField(
        max_length=20,
        choices=skillType.choices,
        default=skillType.GENERAL)
    damage = models.IntegerField(null=True, blank=True)
    max_damage = models.IntegerField(null=True, blank=True)
    healing = models.IntegerField(null=True, blank=True)
    max_healing = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

# character items


class skillSet(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, null=True, blank=True)
    skill = models.ForeignKey('Skill', on_delete=models.CASCADE, null=True, blank=True)
    damage_modifier = models.IntegerField(default=0)
    healing_modifier = models.IntegerField(default=0)
    efficiency = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(10)])

    def __str__(self):
        return f"{self.character} x {self.skill}"


class BackpackItem(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey('Item', on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} (owned by {self.character.character_name})"


class magicTome(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, null=True, blank=True)
    magic = models.ForeignKey('Magic', on_delete=models.CASCADE, null=True, blank=True)
    current_level = models.IntegerField(default=1)
    upgraded_damage = models.IntegerField(default=0)
    upgraded_healing = models.IntegerField(default=0)
    spell_efficiency = models.FloatField(default=0.00, validators=[MinValueValidator(1), MaxValueValidator(10)])


class WeaponBag(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, null=True, blank=True)
    weapon = models.ForeignKey('Weapon', on_delete=models.CASCADE, null=True, blank=True)
    current_durability = models.IntegerField(default=1)
    current_level = models.IntegerField(default=1)
    upgraded_damage = models.IntegerField(default=0)
    weapon_efficiency = models.FloatField(default=0.00, validators=[MinValueValidator(1), MaxValueValidator(10)])

    def __str__(self):
        return f"{self.current_durability} x {self.weapon.name} (owned by {self.character.character_name})"

    def save(self, *args, **kwargs):
        self.weapon_efficiency = min(self.weapon_efficiency, 10.0)
        super().save(*args, **kwargs)


class ArmorBag(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE, null=True, blank=True)
    armor = models.ForeignKey('Armor', on_delete=models.CASCADE, null=True, blank=True)
    current_durability = models.IntegerField(default=1)
    current_level = models.IntegerField(default=1)
    upgraded_defense = models.IntegerField(default=0)
    armor_efficiency = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.current_durability} x {self.armor.name} (owned by {self.character.character_name})"


class Character(models.Model):
    character_name = models.CharField(max_length=50)
    skills = models.ManyToManyField(
        Skill,
        through='skillSet',
        related_name="skill_set",
        blank=True)
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
    armor = models.ManyToManyField(
        Armor,
        through='ArmorBag',
        related_name='armor_bag',
        blank=True
    )
    weapons = models.ManyToManyField(
        Weapon,
        through='WeaponBag',
        related_name='weapon_bag',
        blank=True
    )
    magic = models.ManyToManyField(
        Magic,
        through="magicTome",
        related_name='magic_tome',
        blank=True
    )
    health = models.IntegerField(default=10)
    current_health = models.IntegerField(default=10)
    motivation = models.IntegerField(default=4, validators=[MinValueValidator(0), MaxValueValidator(100)])
    current_motivation = models.IntegerField(default=2)

    def __str__(self):
        return self.character_name

    def delete(self, *args, **kwargs):
        self.backpack.through.objects.filter(character=self).delete()
        self.current_equip_items.through.objects.filter(character=self).delete()

        super().delete(*args, **kwargs)

    def can_advance_rank(self):
        next_rank = Rank.objects.filter(min_level__lte=self.level).exclude(pk=self.rank_id).order_by(
            'min_level').first()
        if next_rank and self.level >= next_rank.min_level:
            return next_rank
        return None

    def advance_rank(self):
        next_rank = self.can_advance_rank()
        if next_rank:
            self.rank = next_rank
            self.save()
            return True
        return False


class CustomUser(AbstractUser):
    number_of_quests = models.IntegerField(default=4)  # changes as you complete quests throughout the day.
    target_num_quests = models.IntegerField(default=2)  # you can have as many quests as you want but this amount is how
    # many you need to complete the day ^
    target_num_quests_inc = models.IntegerField(default=0)  # used to check if target num quests is met
    completed_quests = models.IntegerField(
        default=0)  # increments up 1 when a quest is finished used for the percent_weekly_completed
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
