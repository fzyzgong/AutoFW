from django.db import models

class UserInfo(models.Model):
    id = models.IntegerField
    username = models.CharField(max_length=30,unique=True)
    password = models.CharField(max_length=100)
    authority = models.CharField(max_length=20)#super/common/guest
    createtime = models.DateTimeField()
    remark = models.CharField(max_length=100)
    position = models.CharField(max_length=20)
    gender = models.BooleanField(default=False)

    class Meta:
        db_table = 'userinfo'

class Project(models.Model):
    id = models.IntegerField
    project_code = models.CharField(max_length=20,unique=True)
    project_name = models.CharField(max_length=50)
    PRI = models.CharField(max_length=10)
    create_time = models.DateTimeField()
    creator = models.CharField(max_length=20)
    department = models.CharField(max_length=30)

    class Meta:
        db_table = 'project'


class Project_Module(models.Model):
    project = models.ForeignKey(Project,to_field="project_code")
    module_id = models.CharField(max_length=20)
    module_name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    class Meta:
        db_table = 'project_module'