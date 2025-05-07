from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *



class EquipablesIngredientsInline(admin.TabularInline):
    model = equipablesIngredients
    extra = 1  # Number of empty forms to display initially


class CustomUserAdmin(UserAdmin):
    # Define the fields to display in the admin panel
    list_display = ('username', 'email', 'is_staff', 'is_active')  # Adjust fields as needed
    search_fields = ('username', 'email')  # Allow admin to search by username or email
    ordering = ('username',)  # Order users by username

    # Add fieldsets for the user model in the admin panel
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Add fields when creating a user in the admin panel
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )


class RankAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_level', 'max_level')
    search_fields = ('name',)
    ordering = ('name',)

    fieldsets = (
        ('Name', {'fields': ('name',)}),
        ('Levels', {'fields': ('min_level', 'max_level')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'min_level', 'max_level'),
        }),
    )


class RankDetailsAdmin(admin.ModelAdmin):
    list_display = ('description', 'special_attack', 'special_attack_damage', 'rank')
    search_fields = ('description', 'rank',)
    ordering = ('rank',)

    fieldsets = (
        ('description', {'fields': ('rank', 'description',)}),
        ('attacks', {'fields': ('special_attack', 'special_attack_damage')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('description', 'special_attack', 'special_attack_damage, rank'),
        }),
    )



class DailyQuestAdmin(admin.ModelAdmin):
    list_display = ('quest_name', 'quest_description', 'experience_points', 'drop_class')
    search_fields = ('quest_name',)
    ordering = ('quest_name',)

    fieldsets = (
        ('quest details', {'fields': ('quest_name', 'quest_description', 'experience_points', 'drop_class')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('quest_name', 'quest_description', 'experience_points', 'drop_class'),
        }),
    )


class itemsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'drop_class', 'price', 'type', 'drop_rate', 'marketable', 'market_drop_rate', 'forgeIngredient')
    search_fields = ('name', 'type', 'marketable', 'forgeIngredient')
    ordering = ('name', 'type', 'marketable', 'forgeIngredient')
    fieldsets = (
        ('item details', {'fields': ('name', 'description', 'drop_class', 'price', 'marketable', 'market_drop_rate', 'forgeIngredient')}),
        ('stats', {'fields': ('type', 'drop_rate')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
            'name', 'description', 'drop_class', 'price', 'type', 'drop_rate', 'marketable', 'market_drop_rate', 'forgeIngredient'),
        }),
    )

class skillsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'level_required', 'skill_type', 'damage', 'healing', 'max_damage', 'max_healing')
    search_fields = ('name', 'level_required', 'skill_type')
    ordering = ('name', 'level_required')
    fieldsets = (
        ('item details', {'fields': ('name', 'description')}),
        ('stats', {'fields': ('level_required', 'skill_type', 'damage', 'healing', 'max_damage', 'max_healing')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'name', 'description', 'level_required', 'skill_type', 'damage', 'healing', 'max_damage', 'max_healing'),
        }),
    )


class armorAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'defense', 'resistance', 'forgeable', 'repair_cost')
    search_fields = ('name', 'crafting_ingredients', 'forgeable')
    ordering = ('name',)
    fieldsets = (
        ('armor details', {'fields': ('name', 'description')}),
        ('stats', {'fields': ('defense', 'resistance', 'forgeable', 'repair_cost')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'name', 'description', 'defense', 'resistance', 'crafting_ingredients', 'forgeable', 'repair_cost'),
        }),
    )
    inlines = [EquipablesIngredientsInline]


class weaponAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'damage', 'attack_speed', 'critical_rate', 'forgeable', 'repair_cost')
    search_fields = ('name', 'crafting_ingredients', 'forgeable')
    ordering = ('name',)
    fieldsets = (
        ('weapon details', {'fields': ('name', 'description')}),
        ('stats', {'fields': ('damage', 'attack_speed', 'critical_rate', 'forgeable', 'repair_cost')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'name', 'description', 'damage', 'attack_speed', 'critical_rate', 'crafting_ingredients', 'forgeable', 'repair_cost'),
        }),
    )
    inlines = [EquipablesIngredientsInline]


class magicAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'damage', 'healing', 'special', 'level')
    search_fields = ('name', 'level')
    ordering = ('name', )
    fieldsets = (
        ('magic details', {'fields': ('name', 'description', 'level')}),
        ('stats', {'fields': ('damage', 'healing', 'special')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'name', 'description', 'level', 'damage', 'healing', 'special'),
        }),
    )


class npcAdmin(admin.ModelAdmin):
    list_display = ('name', 'prompt', 'description', 'party', 'is_traveller', 'occupation', 'alignment', 'location',
                    'is_alive', 'level', 'image', 'gender', 'race', 'attitude')
    search_fields = ('name', 'alignment', 'location', 'race')
    ordering = ('name', )
    fieldsets = (
        ('details', {'fields': ('name', 'prompt', 'description', 'party', 'is_traveller', 'occupation', 'alignment', 'location',
                    'is_alive', 'level', 'image', 'gender', 'race', 'attitude')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'name', 'prompt', 'description', 'party', 'is_traveller', 'occupation', 'alignment', 'location',
                'is_alive', 'level', 'image', 'gender', 'race', 'attitude'),
        }),
    )


class questBoardAdmin(admin.ModelAdmin):
    list_display = ('questName', 'questType', 'Difficulty', 'goldValue', 'reputation', 'description', 'can_refresh', 'duration_hours', 'bulletinBoardEntry', 'location')
    search_fields = ('questName', 'Difficulty', 'questType', 'location')
    ordering = ('questName', )
    fieldsets = (
        ('details', {'fields': ('questName', 'questType', 'description', 'bulletinBoardEntry', 'location')}),
        ('stats', {'fields': ('goldValue', 'reputation', 'Difficulty', 'can_refresh', 'duration_hours')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'questName', 'questType', 'Difficulty', 'goldValue', 'reputation', 'description', 'can_refresh', 'bulletinBoardEntry', 'location'),
        }),
    )


class bulletinBoardAdmin(admin.ModelAdmin):
    list_display = ('location', 'message')
    search_fields = ('location', 'message')
    ordering = ('location', 'message')
    fieldsets = (
        ('details', {'fields': ('location', 'message')}),)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('location', 'message'),
        }),
    )



class townsAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'population', 'defense_level', 'monster_threat_level',
                    'reputation', 'chronicle', 'travel_time', 'x', 'y')
    search_fields = ('name', 'population', 'region')
    ordering = ('name', 'region', 'defense_level')
    fieldsets = (
        ('details', {'fields': ('name', 'region', 'population', 'defense_level', 'monster_threat_level',
                    'reputation', 'chronicle', 'travel_time', 'x', 'y')}),)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'region', 'population', 'defense_level', 'monster_threat_level',
                    'reputation', 'chronicle', 'travel_time', 'x', 'y'),
        }),
    )


class npcDialogueAdmin(admin.ModelAdmin):
    list_display = ('npc', 'trigger', 'response', 'condition_flag')
    search_fields = ('npc',)
    ordering = ('npc', 'trigger', 'response', 'condition_flag')
    fieldsets = (
        ('details', {'fields': ('npc', 'trigger', 'response', 'condition_flag')}),)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('npc', 'trigger', 'response', 'condition_flag'),
        }),
    )


class bugAdmin(admin.ModelAdmin):
    list_display = ('title', 'details', 'status')
    search_fields = ('title', 'status')
    ordering = ('title', 'details', 'status')
    fieldsets = (
        ('details', {'fields': ('title', 'details', 'status')}),)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('title', 'details', 'status'),
        }),
    )




admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Rank, RankAdmin)
admin.site.register(RankDetail, RankDetailsAdmin)
admin.site.register(dailyQuest, DailyQuestAdmin)
admin.site.register(Item, itemsAdmin)
admin.site.register(Skill, skillsAdmin)
admin.site.register(Armor, armorAdmin)
admin.site.register(Weapon, weaponAdmin)
admin.site.register(Magic, magicAdmin)
admin.site.register(NPCS, npcAdmin)
admin.site.register(questBoard, questBoardAdmin)
admin.site.register(bulletinBoardExtra, bulletinBoardAdmin)
admin.site.register(towns, townsAdmin)
admin.site.register(NPCDialogueRule, npcDialogueAdmin)
admin.site.register(BugsModel, bugAdmin)





