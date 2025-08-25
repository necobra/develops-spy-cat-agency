from django.db import models


class CompleteChoices(models.TextChoices):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Bread(models.Model):
    external_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)

class SpyCat(models.Model):
    name = models.CharField(max_length=127)
    experience = models.IntegerField()
    bread = models.ForeignKey(Bread, on_delete=models.CASCADE, related_name='spy_cats')
    salary = models.IntegerField()

class Mission(models.Model):
    spy_cat = models.ForeignKey(SpyCat, on_delete=models.CASCADE, related_name='missions')
    complete_state = models.CharField(max_length=127, choices=CompleteChoices, default=CompleteChoices.PENDING)

class Target(models.Model):
    name = models.CharField(max_length=127)
    country = models.CharField(max_length=127)
    notes = models.TextField(blank=True)
    complete_state = models.CharField(max_length=127, choices=CompleteChoices, default=CompleteChoices.PENDING)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='targets')

