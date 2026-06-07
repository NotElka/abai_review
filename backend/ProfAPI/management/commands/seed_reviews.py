# -*- coding: utf-8 -*-
"""Наполнение базы отзывами (в основном положительными).

Запуск:
    py manage.py seed_reviews

Идемпотентно: для пары (студент, преподаватель, предмет) отзыв создаётся один раз.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from ProfAPI.models import Professor, Review, User


# Пул положительных отзывов (рейтинг 4.0–5.0).
POSITIVE = [
    "Отличный преподаватель! Объясняет материал понятно и с интересом. Очень рекомендую.",
    "Очень довольна занятиями. Всегда помогает разобраться в сложных темах.",
    "Лекции структурированы, много полезных примеров. Узнал много нового.",
    "Справедливое оценивание и доброжелательное отношение к студентам.",
    "Пары проходят живо, совсем не скучно. Чувствуется любовь к своему предмету.",
    "Даёт современный и актуальный материал, отвечает на все вопросы. Спасибо!",
    "Грамотный специалист, всегда готов объяснить ещё раз. Однозначно рекомендую.",
    "Интересные семинары и понятная обратная связь по работам.",
    "Один из лучших преподавателей факультета. Многому научился за курс.",
    "Понятная подача и адекватные требования. Учиться комфортно.",
]

# Пул умеренных отзывов (рейтинг ~3.5–4.0) — для естественности.
MODERATE = [
    "Хороший преподаватель, но материала много — к каждой паре нужно готовиться.",
    "Предмет непростой, зато после курса остаются крепкие знания.",
]

# Заранее заданные оценки/сложность по позициям (в основном высокие).
RATINGS = [5.0, 4.5, 5.0, 4.0]
DIFFICULTIES = [3.0, 2.5, 4.0, 3.5]
# Для 4-го (умеренного) отзыва.
MODERATE_RATING = 4.0
MODERATE_DIFFICULTY = 3.5


class Command(BaseCommand):
    help = "Наполняет базу отзывами (преимущественно положительными)"

    @transaction.atomic
    def handle(self, *args, **options):
        students = list(
            User.objects.filter(is_superuser=False)
            .exclude(first_name="")
            .order_by("id")
        )
        if len(students) < 2:
            self.stdout.write(self.style.ERROR(
                "Недостаточно студентов с именами. Сначала создайте пользователей."
            ))
            return

        created = 0
        prof_index = 0

        for professor in Professor.objects.all().order_by("prof_id"):
            subjects = list(professor.subjects.all())
            if not subjects:
                continue

            # 4 отзыва на преподавателя: 3 положительных + 1 умеренный.
            for i in range(4):
                student = students[(prof_index + i) % len(students)]
                subject = subjects[i % len(subjects)]

                if i < 3:
                    rating = RATINGS[i]
                    difficulty = DIFFICULTIES[i]
                    text = POSITIVE[(prof_index + i) % len(POSITIVE)]
                else:
                    rating = MODERATE_RATING
                    difficulty = MODERATE_DIFFICULTY
                    text = MODERATE[prof_index % len(MODERATE)]

                _, was_created = Review.objects.get_or_create(
                    user=student,
                    professor=professor,
                    subject=subject,
                    defaults={
                        "rating": rating,
                        "difficulty": difficulty,
                        "text": text,
                        "is_anounimous": False,
                    },
                )
                if was_created:
                    created += 1

            prof_index += 1

        self.stdout.write(self.style.SUCCESS(
            f"Готово. Отзывов добавлено: {created}. Всего отзывов: {Review.objects.count()}."
        ))
