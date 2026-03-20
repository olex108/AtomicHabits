from datetime import timedelta

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Habit(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    place = models.CharField(max_length=50, verbose_name="Место")
    time = models.TimeField(verbose_name="Время")
    action = models.TextField(verbose_name="Действие")
    is_pleasant_habit = models.BooleanField(verbose_name="Приятная привычка")
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"is_pleasant_habit": True},
        related_name="dependent_habits",
        verbose_name="Связанная привычка",
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1, verbose_name="Периодичность (день)", validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    reward = models.TextField(verbose_name="Вознаграждение", null=True, blank=True)
    complete_time = models.DurationField(
        verbose_name="Время на выполнение",
        validators=[MaxValueValidator(timedelta(seconds=120))],
        default=timedelta(seconds=120),
    )
    is_public = models.BooleanField(verbose_name="Признак публичности")

    def __str__(self):
        return self.action

    # def clean(self):
    #     super().clean()
    #     if self.is_pleasant_habit and self.related_habit:
    #         raise ValidationError({
    #             'related_habit': 'У приятной привычки не может быть связанной привычки.'
    #         })
    #
    #     if self.related_habit and not self.related_habit.is_pleasant_habit:
    #         raise ValidationError({
    #             'related_habit': 'В связанные привычки можно добавлять только привычки с признаком приятной.'
    #         })
    #
    #     if self.reward and self.related_habit:
    #         raise ValidationError({
    #             'reward': 'В модели не должно быть заполнено одновременно и поле вознаграждения, '
    #                       'и поле связанной привычки. Можно заполнить только одно из двух полей'
    #         })

    class Meta:
        verbose_name = "привычка"
        verbose_name_plural = "привычки"
        ordering = ["user"]
