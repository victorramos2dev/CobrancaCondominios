from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]
    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False)),
                ('username', models.CharField(max_length=150, unique=True)),
                ('nome', models.CharField(blank=True, max_length=100)),
                ('telefone', models.CharField(blank=True, max_length=20)),
                ('tipo', models.CharField(
                    choices=[('administrador', 'Administrador'), ('usuario', 'Usuário')],
                    default='usuario', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, related_name='usuario_set', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='usuario_set', to='auth.permission')),
            ],
            options={'db_table': 'Usuarios', 'verbose_name': 'Usuário', 'verbose_name_plural': 'Usuários'},
        ),
    ]
