
from django.db import models

class Novel(models.Model):
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=20)
    img = models.CharField(max_length=255)
    status = models.CharField(max_length=10)
    people = models.CharField(max_length=10)
    chapter = models.IntegerField()
    sort = models.IntegerField()
    type = models.CharField(max_length=20)
    list = models.CharField(max_length=20)
    class Meta:
        db_table = 'novel'  # 设置自定义表名
    def __str__(self):
        return self.title
