import os
import click
from flask.cli import with_appcontext
from flask_security.utils import hash_password

from .app import db, user_datastore
from .models import Contact, Conference, Participant, ParticipantProfile, ConferenceProfile

def register_commands(app):
    """Регистрирует современные CLI-команды во Flask приложении."""

    @app.cli.command("create-schema")
    @with_appcontext
    def create_schema_command():
        """Создание всех таблиц базы данных."""
        db.create_all()
        click.echo("Таблицы базы данных успешно созданы.")

    @app.cli.command("create-admin")
    @with_appcontext
    def create_admin_command():
        """Создание ролей и суперпользователя admin (идемпотентная команда)."""
        # Получаем пароль из переменной окружения
        admin_password = os.environ.get("ADMIN_PASSWORD")
        if not admin_password:
            click.echo("ERROR: ADMIN_PASSWORD environment variable is required and must be non-empty.", err=True)
            raise click.Abort()

        # Создаём или получаем роли
        admin_role = user_datastore.find_or_create_role(
            name="admin",
            description="System administrator",
        )
        user_role = user_datastore.find_or_create_role(
            name="user",
            description="Conference user",
        )

        # Ищем существующего пользователя admin
        admin = user_datastore.find_user(username="admin")

        # Создаём, только если ещё не существует
        if not admin:
            admin = user_datastore.create_user(
                username="admin",
                password=hash_password(admin_password),
            )

        # Добавляем роль admin пользователю, если её ещё нет
        if admin_role not in getattr(admin, "roles", []):
            user_datastore.add_role_to_user(admin, admin_role)

        db.session.commit()
        click.echo("Роли и пользователь admin успешно созданы/обновлены.")

    @app.cli.command("init")
    @with_appcontext
    def init_command():
        """Полный сброс структуры БД и наполнение чистыми строковыми тестовыми данными."""
        # Получаем пароли из переменных окружения
        admin_password = os.environ.get("ADMIN_PASSWORD")
        user_password = os.environ.get("USER_PASSWORD")

        if not admin_password:
            click.echo("ERROR: ADMIN_PASSWORD environment variable is required and must be non-empty.", err=True)
            raise click.Abort()

        if not user_password:
            click.echo("ERROR: USER_PASSWORD environment variable is required and must be non-empty.", err=True)
            raise click.Abort()

        click.echo("Сброс и инициализация базы данных...")
        db.drop_all()
        db.create_all()

        # Создание ролей
        user_datastore.create_role(name='admin', description='System administrator')
        user_datastore.create_role(name='user', description='Conference user')

        # Создание тестовых пользователей
        admin = user_datastore.create_user(username='admin', email="admin@test.com", password=hash_password(admin_password))
        user = user_datastore.create_user(username='user', email="user@test.com", password=hash_password(user_password))

        user_datastore.add_role_to_user(admin, 'admin')
        user_datastore.add_role_to_user(user, 'user')

        # Тестовые контакты (строки без gettext)
        contacts = [
            ('1010', 'John Smith'),
            ('1020', 'Sam Brown'),
        ]
        for phone, name in contacts:
            rec = Contact(phone=phone, name=name, user=admin)
            db.session.add(rec)

        # Тестовые профили участников
        guest_user_profile = ParticipantProfile(name='Guest', startmuted=True)
        db.session.add(guest_user_profile)
        marked_user_profile = ParticipantProfile(name='Marker', marked=True)
        db.session.add(marked_user_profile)
        admin_user_profile = ParticipantProfile(name='Administrator', admin=True)
        db.session.add(admin_user_profile)

        # Профиль конференции
        conf_profile = ConferenceProfile(name='Default')
        db.session.add(conf_profile)

        # Тестовая конференция
        conf = Conference(
            number=100,
            name='Test Conference',
            conference_profile=conf_profile,
            public_participant_profile=guest_user_profile,
            is_public=True,
            user=admin,
        )
        db.session.add(conf)

        # Участники конференции
        p1 = Participant(conference=conf, profile=admin_user_profile, phone='1001', user=admin)
        p2 = Participant(conference=conf, profile=guest_user_profile, phone='1002', user=admin)
        p3 = Participant(conference=conf, profile=marked_user_profile, phone='1003', user=admin)
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)

        # Сохранение изменений в БД
        db.session.commit()
        click.echo("База данных успешно инициализирована тестовыми данными!")

    @app.cli.command("start-conf")
    @click.argument("conf_num")
    @with_appcontext
    def start_conf_command(conf_num):
        """Запуск конференции по её номеру из CLI."""
        conf = Conference.query.filter_by(number=conf_num).first()
        if conf:
            conf.invite_participants()
            click.echo(f"Конференция {conf_num} запущена.")
        else:
            click.echo(f"Конференция {conf_num} не найдена.")
