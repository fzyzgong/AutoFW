from django.db import models

class UserInfo(models.Model):
    id = models.IntegerField
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=100)
    authority = models.CharField(max_length=20)#super/common/guest
    createtime = models.DateTimeField()
    remark = models.CharField(max_length=100)
    position = models.CharField(max_length=20)
    gender = models.BooleanField(default=False)