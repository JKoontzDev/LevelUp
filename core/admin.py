from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


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
    list_display = ('name', 'description', 'drop_class', 'price', 'type', 'damage', 'healing', 'drop_rate', 'marketable', 'market_drop_rate')
    search_fields = ('name', 'type', 'marketable')
    ordering = ('name', 'type', 'marketable')
    fieldsets = (
        ('item details', {'fields': ('name', 'description', 'drop_class', 'price', 'marketable', 'market_drop_rate')}),
        ('stats', {'fields': ('type', 'damage', 'healing', 'drop_rate')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
            'name', 'description', 'drop_class', 'price', 'type', 'damage', 'healing', 'drop_rate', 'marketable', 'market_drop_rate'),
        }),
    )

class skillsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'level_required', 'damage', 'healing')
    search_fields = ('name', 'level_required')
    ordering = ('name', 'level_required')
    fieldsets = (
        ('item details', {'fields': ('name', 'description')}),
        ('stats', {'fields': ('level_required', 'damage', 'healing')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'name', 'description', 'level_required', 'damage', 'healing'),
        }),
    )





admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Rank, RankAdmin)
admin.site.register(RankDetail, RankDetailsAdmin)
admin.site.register(dailyQuest, DailyQuestAdmin)
admin.site.register(Item, itemsAdmin)
admin.site.register(Skill, skillsAdmin)




