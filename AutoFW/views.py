#coding=utf-8
import json

import datetime
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from models import *
from django.core import serializers
import MySQLdb

def login(request):
    return render(request, 'AutoFW/login.html')

#登录验证用户名是否存在
def login_check_name(request):
    uname = request.GET.get('username')
    count = UserInfo.objects.filter(username=uname).count()
    return JsonResponse({'count': count})

#登录验证该用户名的密码是否存在
def login_check_passwd(request):
    upasswd = request.POST.get('password')
    username = request.POST.get('username')
    # s1=sha1()
    # s1.update(upasswd)
    # upasswd = s1.hexdigest()
    count = UserInfo.objects.filter(username=username,password=upasswd).count()
    return JsonResponse({'count':count})

#验证用户名和密码是否正确
def login_handle(request):
    post = request.POST
    user = post.get('username')
    passwd = post.get('password')

    users = UserInfo.objects.filter(username=user)

    conn = MySQLdb.connect(host='localhost',port=3306,db='autofw',user='root',passwd='123456',charset='utf8')

    handle = conn.cursor()

    username = handle.execute("select username from userinfo where username='%s'" % user)
    username = handle.fetchone()

    password = handle.execute("select password from userinfo where username='%s'" % user)
    password = handle.fetchone()

    print ("username:"+str(username)+"  password:"+str(password))

    #判断元组是否为空，空为false
    if(username and password):
        print ("user:"+user+"  passwd:"+passwd)
        if(username[0]==user and password[0]==passwd):
            username = username[0]
            position = UserInfo.objects.filter(username=username)
            print (str(position[0].position))
            position = position[0].position

            context = {'username':username,'position':position}

            return render(request,'AutoFW/easyui_workbench.html')
        else:
            # return HttpResponse("username or passwd1 error")
            return render(request, 'AutoFW/login.html')
    else:
        # return HttpResponse("username or passwd error")
        return render(request, 'AutoFW/login.html')


def project_manage(request):
    return render(request,'AutoFW/easyui_project_manage.html')

class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                 return obj.struct_time('%Y-%m-%d %H:%M:%S')
            elif isinstance(obj, datetime.date):
                da = str(obj.strftime('%Y-%m-%d'))
                #return obj.strftime('%Y-%m-%d')
                return da
            else:
                return json.JSONEncoder.default(self, obj)
        except Exception,e:
            print e
#datagrid
def Read_all_SQL(request):
    obj_all = Project.objects.all()
    eaList = []
    for li in obj_all:
        #序列化
        datetimeformat = json.dumps(str(li.create_time))
        create_time = datetimeformat.split('"')[1].split('+')[0]
        # print create_time
        eaList.append(
            {"project_id": li.project_code, "project_name": li.project_name, "creator": li.creator, "create_time": create_time,
             "prioirty": li.PRI,"department": li.department,"id": li.id})
    eaList_len = json.dumps(len(eaList),cls=CJsonEncoder)
    # print (str(eaList))
    json_data_list = {'rows': eaList, 'total': eaList_len}

    easyList = json.dumps(json_data_list,cls=CJsonEncoder)
    # print (easyList)
    return HttpResponse(easyList)

# Edit_UserName
def Edit_UserNmae(request, id):
    print(id)
    print(request.method)
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        project_name = request.POST.get('project_name')
        creator = request.POST.get('creator')
        create_time = request.POST.get('create_time')
        prioirty = request.POST.get('prioirty')
        department = request.POST.get('department')
        dic = {'project_code': project_id, 'project_name': project_name,
               'creator': creator, 'create_time': create_time,'PRI':prioirty,'department':department};
        print(str(dic))
        Project.objects.filter(id=id).update(**dic)
        return HttpResponse("Edit_OK")


def income_project(request, project_id):
    print ("income_project" + str(project_id))

    module = Project_Module.objects.filter(project=project_id)

    context = {"project_id":project_id,'list':module}

    return render(request,'AutoFW/workon_project.html',context)


def project_attribute(request):
    project_id = request.GET.get('project_id')
    print ("project_attribute"+str(project_id))
    # rs = Project.objects.filter(project_code=project_id)
    rs = Project.objects.get(project_code=project_id)
    create_time = rs.create_time
    creator = rs.creator
    department = rs.department
    prioirty = rs.PRI
    project_name =rs.project_name
    # 序列化
    datetimeformat = json.dumps(str(create_time))
    create_times = datetimeformat.split('"')[1].split(' ')[0]


    print (str(create_times))
    # 把Unicode转成str
    print (str(creator.encode("utf8")))
    print (str(department.encode("utf8")))
    print (prioirty.encode("utf8"))
    print (str(project_name.encode("utf8")))

    content={'create_time':create_times,'creator':creator,
              'department':department,'prioirty':prioirty,'project_name':project_name}

    return JsonResponse(content)


def module_append(request):
    project_id = request.GET.get('project_id')
#     print ("module_append" + str(project_id))
    module = Project_Module.objects.filter(project=project_id)
#     # list = []
#     # for module in data:
#     #     list.append([module.module_name])
    content = {'list':module}
#     # print (list)
    return render(request,'AutoFW/workon_project.html',content)


# add User_Name  + start_app
def app_start(request):
    # add_save_user
    if request.method == "POST":
        print("POST")
        print(request.POST)
        project_id = request.POST.get('project_id')
        project_name = request.POST.get('project_name')
        creator = request.POST.get('creator')
        create_time = request.POST.get('create_time')
        prioirty = request.POST.get('prioirty')
        department = request.POST.get('department')
        dic = {'project_code': project_id, 'project_name': project_name,
               'creator': creator, 'create_time': create_time,'PRI':prioirty,'department':department};
        Project.objects.create(**dic)

        return HttpResponse("save")
    else:
        print(" is null_!")
    return render(request, 'AutoFW/easyui_project_manage.html')

# Remove SQL_ID
def Remove_US_ID(request):
    if request.method == "POST":
        print("REMOVE POST")
        print(request.POST.get('id'))
        us_id = request.POST.get('id')
        Project.objects.filter(id=us_id).delete()
    return HttpResponse("REMOVE")


def module_Read_all_SQL(request,project_id):
    obj_module_all = Project_Module.objects.filter(project_id=project_id)
    eaList = []
    for list in obj_module_all:
        eaList.append(
            {"module_id": list.module_id, "module_name": list.module_name, "description": list.description,
             "project_id": list.project_id})
    eaList_len = json.dumps(len(eaList), cls=CJsonEncoder)
    # print (str(eaList))
    json_data_list = {'rows': eaList, 'total': eaList_len}

    easyList = json.dumps(json_data_list, cls=CJsonEncoder)
    # print (easyList)
    return HttpResponse(easyList)


def Module_start(request,project_id):
    if request.method == "POST":
        print("POST")
        # print(request.POST)
        module_id = request.POST.get('module_id')
        module_name = request.POST.get('module_name')
        description = request.POST.get('description')

#project_id 是外键 本应是project
        dic = {'project_id': project_id,'module_id': module_id, 'module_name': module_name,
               'description': description}

        # m = Project_Module()
        # m.module_id=module_id
        # print ('module_id')
        # m.module_name=module_name
        # print ('module_name')
        # m.description=description
        # print ('description')
        # m.project_id=project_id
        # print ('project')
        # m.save()

        Project_Module.objects.create(**dic)

        return HttpResponse("save")
    else:
        print(" is null_!")
    return render(request, 'AutoFW/easyui_project_manage.html')

#module_id不能编辑，module_id为主键，但前端显示能编辑，由于用的是easyui框架，不能实现单个菜单栏不能编辑成distable,只能退而求次用module_id
#为filter条件，另一种方法就是更改表结构，新增一个pk值，通过url传过来作为filter值
def  Edit_Module(request,module_id,project_id):
    print(module_id)
    print(request.method)
    if request.method == 'POST':
        module_id = request.POST.get('module_id')
        module_name = request.POST.get('module_name')
        description = request.POST.get('description')
        # project_id = request.POST.get('project_id')

        dic = {'module_id': module_id, 'module_name': module_name,
               'description': description, 'project_id': project_id};
        print(str(dic))
        Project_Module.objects.filter(module_id=module_id).update(**dic)

        return HttpResponse("Edit_OK")

# Remove SQL_ID
def Remove_Module(request):
    if request.method == "POST":
        print("REMOVE id")
        print(request.POST.get('id'))
        module_id = request.POST.get('id')
        Project_Module.objects.filter(module_id=module_id).delete()
    return HttpResponse("REMOVE")