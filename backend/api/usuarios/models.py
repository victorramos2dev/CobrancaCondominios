from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UsuarioManager(BaseUserManager):
    def create_user(self, username, password=None, **extra):
        if not username:
            raise ValueError('Username obrigatório')
        user = self.model(username=username, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra):
        extra.setdefault('tipo', 'administrador')
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra)


class Usuario(AbstractBaseUser, PermissionsMixin):
    TIPO_CHOICES = [
        ('administrador', 'Administrador'),
        ('usuario', 'Usuário'),
    ]

    username  = models.CharField(max_length=150, unique=True)
    nome      = models.CharField(max_length=100, blank=True)
    telefone  = models.CharField(max_length=20, blank=True)
    tipo      = models.CharField(max_length=50, choices=TIPO_CHOICES, default='usuario')
    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table  = 'Usuarios'
        verbose_name        = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.tipo == 'administrador'
