# -*- coding: utf-8 -*-
"""Наполнение базы преподавателями и предметами.

Запуск:
    py manage.py seed_data
    py manage.py seed_data --flush   # очистить предметы/преподавателей перед добавлением

Команда идемпотентна: повторный запуск не создаёт дубликатов.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from ProfAPI.models import Professor, Subject


# Структура данных: преподаватель -> список предметов (название, описание).
# Описание предмета: "<курс> · <образовательная программа>".
SEED = [
    {
        "name": "Миажден С.А.",
        "description": "Преподаватель факультета истории",
        "subjects": [
            ("Международные организации и региональная интеграция", "4 курс · Научная история"),
            ("История Западного Средневековья", "2 курс · Научная история"),
            ("Методологии исторического исследования", "4 курс · География-история"),
            ("Средневековой Восток", "2 курс · Научная история"),
            ("Шығыс елдерінің жаңа және қазіргі заман тарихы", "2, 3 курс · Тарих-география"),
            ("Ежелгі өркениеттер мен антикалық дәуір", "1 курс · Тарих-қоғамтану"),
            ("Центральная Азия в современной системе международных отношений", "3 курс · Научная история"),
            ("Тюркские народы: история и современность", "2 курс · Ғылыми тарих"),
            ("Бағалау және дамыту", "3 курс · Тарих-география"),
            ("Шетел тарихының тарихнамасы мен дерекнамасы", "3 курс · Тарих-дінтану"),
            ("Ортағасырлар тарихы (Батыс + Шығыс)", "3 курс · География-тарих"),
        ],
    },
    {
        "name": "Шорманова А.К.",
        "description": "Лектор факультета истории",
        "subjects": [
            ("Планирование и преподавание", "3 курс · История-обществознание"),
        ],
    },
    {
        "name": "Сутеева Х.А.",
        "description": "Лектор факультета истории",
        "subjects": [
            ("Цивилизация востока в новое время", "3 курс · Ғылыми тарих"),
            ("Шет елдердің деректануы және тарихнамасы", "3 курс · Тарих-дінтану"),
        ],
    },
    {
        "name": "Нұрмұхан Е.Т.",
        "description": "Лектор факультета истории",
        "subjects": [
            ("Ежелгі дүние тарихы", "1 курс · Ғылыми тарих"),
        ],
    },
    {
        "name": "Тлеубаев Ш.Б.",
        "description": "Лектор факультета истории",
        "subjects": [
            ("Еуропа және Америка елдерінің жаңа және қазіргі заман тарихы", "3 курс · Ғылыми тарих"),
        ],
    },
    {
        "name": "Қырғызсхан Г.А.",
        "description": "Лектор факультета истории",
        "subjects": [
            ("Батыс елдерінің жаңа және қазіргі заман тарихы", "3 курс · Тарих-дінтану"),
        ],
    },
]


class Command(BaseCommand):
    help = "Наполняет базу преподавателями и предметами"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Удалить существующих преподавателей и предметы перед добавлением",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            deleted_profs = Professor.objects.all().delete()[0]
            deleted_subjs = Subject.objects.all().delete()[0]
            self.stdout.write(
                self.style.WARNING(
                    f"Очищено: преподавателей {deleted_profs}, предметов {deleted_subjs}"
                )
            )

        profs_created = 0
        subjs_created = 0
        links_added = 0

        for entry in SEED:
            professor, created = Professor.objects.get_or_create(
                name=entry["name"],
                defaults={"description": entry["description"]},
            )
            if created:
                profs_created += 1
            elif not professor.description and entry["description"]:
                professor.description = entry["description"]
                professor.save(update_fields=["description"])

            for subj_name, subj_desc in entry["subjects"]:
                subject, s_created = Subject.objects.get_or_create(
                    name=subj_name,
                    defaults={"description": subj_desc},
                )
                if s_created:
                    subjs_created += 1
                elif not subject.description and subj_desc:
                    subject.description = subj_desc
                    subject.save(update_fields=["description"])

                if not professor.subjects.filter(pk=subject.pk).exists():
                    professor.subjects.add(subject)
                    links_added += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово. Преподавателей добавлено: {profs_created}, "
                f"предметов добавлено: {subjs_created}, связей создано: {links_added}."
            )
        )
