# -*- coding: utf-8 -*-
"""Создание демонстрационных пользователей-студентов.

Запуск:
    py manage.py seed_users

Идемпотентно: повторный запуск обновляет существующих, не создавая дублей.
"""
from django.core.management.base import BaseCommand

from ProfAPI.models import User


USERS = [
    ("aibek",  "Aibek2024!",  "Айбек",  "Нурланов",  "aibek@abai.edu.kz",  2),
    ("dana",   "Dana2024!",   "Дана",   "Сериккызы", "dana@abai.edu.kz",   3),
    ("timur",  "Timur2024!",  "Тимур",  "Касымов",   "timur@abai.edu.kz",  1),
    ("aru",    "Aru2024!",    "Аружан", "Болатова",  "aru@abai.edu.kz",    4),
    ("yerlan", "Yerlan2024!", "Ерлан",  "Тлеген",    "yerlan@abai.edu.kz", 2),
]


class Command(BaseCommand):
    help = "Создаёт демонстрационных пользователей-студентов"

    def handle(self, *args, **options):
        created = 0
        for username, password, first, last, email, course in USERS:
            user, was_created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "email": email,
                    "course": course,
                },
            )
            user.first_name = first
            user.last_name = last
            user.email = email
            user.course = course
            user.set_password(password)
            user.save()
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Готово. Пользователей создано: {created}. Всего: {User.objects.count()}."
        ))
