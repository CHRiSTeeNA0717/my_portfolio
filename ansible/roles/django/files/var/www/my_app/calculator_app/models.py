from django.db import models

# Create your models here.

class Electric(models.Model):
    date_electric_start = models.DateField(unique=True, primary_key=True)
    date_electric_end = models.DateField(unique=True)
    room_A = models.IntegerField()
    room_B = models.IntegerField()
    room_CShare = models.IntegerField()
    room_D = models.IntegerField()
    room_E = models.IntegerField()
    room_F = models.IntegerField()

class Water(models.Model):
    date_water_start = models.DateField(unique=True, primary_key=True)
    date_water_end = models.DateField(unique=True)
    amount = models.IntegerField()

class Gas(models.Model):
    date_gas_start = models.DateField(unique=True, primary_key=True)
    date_gas_end = models.DateField(unique=True)
    amount = models.IntegerField()

class Room(models.Model):
    date_room = models.DateField(unique=True, primary_key=True)
    amount_electric = models.ForeignKey(Electric, to_field="date_electric_start",on_delete=models.SET_NULL, null=True)
    amount_water = models.ForeignKey(Water, to_field="date_water_start", on_delete=models.SET_NULL, null=True)
    amount_gas = models.ForeignKey(Gas, to_field="date_gas_start", on_delete=models.SET_NULL, null=True)
    A = models.CharField(max_length=255, null=True)
    B = models.CharField(max_length=255, null=True)
    C = models.CharField(max_length=255, null=True)
    D = models.CharField(max_length=255, null=True)
    E = models.CharField(max_length=255, null=True)
    F = models.CharField(max_length=255, null=True)
    G = models.CharField(max_length=255, null=True)
    H = models.CharField(max_length=255, null=True)
    I = models.CharField(max_length=255, null=True)
    J = models.CharField(max_length=255, null=True)
    K = models.CharField(max_length=255, null=True)

class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="")