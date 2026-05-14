from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model         = Usuario
    list_display  = ['username', 'nome', 'tipo', 'is_active', 'is_staff']
    list_filter   = ['tipo', 'is_active']
    search_fields = ['username', 'nome']
    ordering      = ['username']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Dados pessoais', {'fields': ('nome', 'telefone', 'tipo')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'nome', 'telefone', 'tipo', 'password1', 'password2')}),
    )
