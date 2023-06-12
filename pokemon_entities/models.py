from django.db import models  # noqa F401
from django.utils import timezone


class Pokemon(models.Model):
    title = models.CharField('Имя покемона', max_length=200)
    title_en = models.CharField(
        'Имя на английском',
        max_length=200,
        null=True, blank=True)
    title_jp = models.CharField(
        'Имя на японском',
        max_length=200,
        null=True, blank=True)
    image = models.ImageField('Изображение', null=True, blank=True)
    description = models.TextField('Описание', null=True, blank=True)
    previous_evolution = models.ForeignKey(
        'self',
        verbose_name='Из кого эволюционирует',
        on_delete=models.SET_NULL,
        related_name='next_evolutions',
        null=True, blank=True)

    def __str__(self):
        return self.title


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(
        Pokemon,
        verbose_name='Покемон',
        related_name='entities',
        on_delete=models.CASCADE)

    lat = models.FloatField('Ширина')
    lon = models.FloatField('Длина')

    appeared_at = models.DateTimeField('Когда появился')
    disappeared_at = models.DateTimeField('Когда исчезнет')

    level = models.IntegerField('Уровень')

    health = models.IntegerField('Здоровье', null=True, blank=True)
    strength = models.IntegerField('Сила', null=True, blank=True)
    defence = models.IntegerField('Защита', null=True, blank=True)
    stamina = models.IntegerField('Выносливость', null=True, blank=True)

    def __str__(self):
        return f'{self.pokemon.title}, ур. {self.level}'
