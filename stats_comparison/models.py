from django.db import models

# Create your models here.

class Country(models.Model):
    code = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Indicator(models.Model):
    code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class StatisticValue(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    year = models.IntegerField()
    value = models.FloatField(null=True)
    
    class Meta:
        unique_together = ('country', 'indicator', 'year')
        indexes = [
            models.Index(fields=['country', 'indicator', 'year']),
        ]
