from django.db import models

# Create your models here.

class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    price = models.FloatField()
    eps = models.FloatField()
    pe_ratio = models.FloatField()
    valuation = models.CharField(max_length=10)