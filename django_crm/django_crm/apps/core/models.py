from django.db import models


class CRMBaseModel(models.Model):
    class Meta:
        abstract = True
