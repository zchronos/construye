# -*- coding: utf-8 -*-
from django.db import models

class Mapa(models.Model):
    Coordenada = models.CharField(max_length=20)