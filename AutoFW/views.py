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

    # users = UserInfo.objects.filter(username=user)

    conn = MySQLdb.connect(host='localhost',port=3306,db='autofw',user='root',passwd='123456',charset='utf8')

    handle = conn.cursor()

    username = handle.execute("select username from userinfo where username='%s'" % user)
    username = handle.fetchone()

    password = handle.execute("select password from userinfo where username='%s'" % user)
    password = handle.fetchone()

    print ("username:"+str(username)+"  password:"+str(password))

    #判断元组是否为空，空为false
    if(username and password):
        # print ("user:"+user+"  passwd:"+passwd)
        if(username[0]==user and password[0]==passwd):
            username = username[0]
            position = UserInfo.objects.filter(username=username)
            # print (str(position[0].position))
            position = position[0].position

            context = {'username':username,'position':position}

            return render(request,'AutoFW/easyui_workbench.html',context)
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
#显示所有项目信息在前端展示
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
    print ("income_project:" + str(project_id))
    #获取该项目所有模块对象list
    module = Project_Module.objects.filter(project=project_id)
    #用来装模块名字
    module_name_list = []
    case_count_list = []
    case_pass_count = ""
    case_failed_count = ""
    case_none_count = ""

    for list in module:
        module_name_list.append(list.module_name)
        #获取每个模块的总用例数
        module_case_count = Project_Case.objects.filter(module_name=list.module_name).count()


        #该模块测试状态统计（PASS/FAILED/NONE）
        #该模块测试用例通过的总个数
        case_pass_count = Project_Case.objects.filter(module_name=list.module_name).filter(description="PASS").count()

        #该模块测试用例失败的总个数
        case_failed_count = Project_Case.objects.filter(module_name=list.module_name).filter(description="FAILED").count()

    #     #该模块测试用例未测的总个数
        case_none_count = Project_Case.objects.filter(module_name=list.module_name).filter(description="NONE").count()

        module_case_count={"pass":case_pass_count,"failed":case_failed_count,"none":case_none_count}

        case_count_list.append(module_case_count)
    print (case_count_list)
    # print ("case_pass_count:" + str(case_pass_count))
    # print ("case_failed_count:" + str(case_failed_count))
    # print ("case_none_count:" + str(case_none_count))

    # 转成字典
    module_case_count_dir = dict(zip(module_name_list,case_count_list))

    print ("module_case_count_list-----"+str(module_case_count_dir))

    context = {"project_id":project_id,'list':module_case_count_dir}

    return render(request,'AutoFW/workon_project.html',context)


def project_attribute(request):
    project_id = request.GET.get('project_id')
    print ("project_attribute"+str(project_id))
    # rs = Project.objects.filter(project_code=project_id)
    #获取项目信息
    rs = Project.objects.get(project_code=project_id)
    create_time = rs.create_time
    creator = rs.creator
    department = rs.department
    prioirty = rs.PRI
    project_name =rs.project_name
    # 序列化
    datetimeformat = json.dumps(str(create_time))
    create_times = datetimeformat.split('"')[1].split(' ')[0]

    #获取模块总数
    project_module_count = Project_Module.objects.filter(project=project_id).count()
    print ("module_count:"+str(project_module_count))

    #获取项目API接口总数
    project_case_count = Project_Case.objects.filter(project_name=project_name).count()
    print ("project_case_count:" + str(project_case_count))

    # print (str(create_times))
    # # 把Unicode转成str
    # print (str(creator.encode("utf8")))
    # print (str(department.encode("utf8")))
    # print (prioirty.encode("utf8"))
    # print (str(project_name.encode("utf8")))

    content={'create_time':create_times,'creator':creator,
              'department':department,'prioirty':prioirty,'project_name':project_name,
             'project_module_count':project_module_count,'project_case_count':project_case_count}

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
        #获取每个模块下api接口有多少个
        module_case_count = Project_Case.objects.filter(module_name=list.module_name).count()
        eaList.append(
            {"module_id": list.module_id, "module_name": list.module_name, "description": list.description,
             "project_id": list.project_id,"module_count":module_case_count})
        # module_case_dir={list.module_name:Project_Case.objects.filter(module_name=list.module_name).count()}

    # print (str(module_case))
    print (str(eaList))

    eaList_len = len(eaList)

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


#接口管理进入入口
def workon_tabs_api(request,project_id):
    # 获取项目模块list，传递给前端提供给form表单用
    module_name_list = Project_Module.objects.filter(project=project_id).values('module_name')
    # print (module_name_list)
    return render(request,'AutoFW/workon_tabs_api_curd.html',{"project_id":project_id,"module_name_list":module_name_list})


def case_Read_all_SQL(request,project_id):
    obj_project = Project.objects.filter(project_code=project_id)
    obj_project_name = obj_project.values('project_name')

    project_case_all = Project_Case.objects.filter(project_name=obj_project_name)

    # test1 = project_case_all.values('project_name')[0]['project_name']
    # module_name = project_case_all.values('module_name')[0]['module_name']
    # print (module_name)

    caseList = []
    for list in project_case_all:

        #project_name module_name为外键，单独获取 方法一
        i = 0
        # project_name = project_case_all.values('project_name')[i]['project_name']
        # module_name = project_case_all.values('module_name')[i]['module_name']
        #获取外键指定值 module_name project_name 方法二
        # print (list.module_name.module_name)
        caseList.append({"case_id":list.case_id,"module_name":list.module_name.module_name,"project_name":list.project_name.project_name,
                         "case_name":list.case_name,"creator":list.creator,"url_path":list.url_path,
                         "method":list.method,"parameter":list.parameter,"expected":list.expected,
                         "description":list.description})
        # i += 1

    caseList_len = len(caseList)
    # print (str(caseList))
    json_data_case_list = {'rows':caseList,'total':caseList_len}
    #序列化
    case_list = json.dumps(json_data_case_list,cls=CJsonEncoder)
    return HttpResponse(case_list)


def API_start(request,project_id):
    if request.method == "POST":
        print("POST")
        case_id = request.POST.get('case_id')
        module_name = request.POST.get('module_name')

        #获取项目名，传递给前端
        project_name = Project.objects.filter(project_code=project_id).values('project_name')[0]['project_name']

        case_name = request.POST.get('case_name')
        creator = request.POST.get('creator')
        url_path = request.POST.get('url_path')
        method = request.POST.get('method')
        parameter = request.POST.get('parameter')
        expected = request.POST.get('expected')
        description = request.POST.get('description')
        # module_name_id是外键 本应是module_name    project_name_id是外键 本应是project_name
        dic = {'case_id': case_id,'module_name_id': module_name, 'project_name_id':project_name,
               'case_name': case_name,'creator':creator,'url_path':url_path,'method':method,
               'parameter':parameter,'expected':expected,'description':description}

        Project_Case.objects.create(**dic)

        return HttpResponse("save")
    else:
        print(" is null_!")
    return render(request, 'AutoFW/workon_project.html')


def editAPI(request,project_id):
    if request.method == "POST":
        print ("editAPI submit")
        case_id = request.POST.get('case_id')
        case_name = request.POST.get('case_name')
        url_path = request.POST.get('url_path')
        method = request.POST.get('method')
        parameter = request.POST.get('parameter')
        expected = request.POST.get('expected')
        module_name = request.POST.get('module_name')
        description = request.POST.get('description')
        # print (module_name)
        creator = request.POST.get('creator')

        project_name = Project.objects.filter(project_code=project_id).values('project_name')[0]['project_name']

        dic = {'case_id': case_id, 'case_name': case_name,
               'url_path': url_path, 'method': method,
               'parameter': parameter, 'expected': expected,
               'module_name': module_name, 'project_name': project_name,
               'description': description};
        print(str(dic))
        Project_Case.objects.filter(case_id=case_id).update(**dic)

    return HttpResponse("save")


def removeAPI(request):
    if request.method == "POST":
        print("REMOVE API")
        print(request.POST.get('id'))
        case_id = request.POST.get('id')
        Project_Case.objects.filter(case_id=case_id).delete()
    return HttpResponse("REMOVE")


#用户信息管理
def user_manage(request,username):
    #获取登录用户信息权限，是否能够访问用户信息管理页面
    authority = UserInfo.objects.filter(username=username)[0].authority
    if(authority=='superman'):
        print (authority+" access the user information management page!")

        return render(request,"AutoFW/workbench_userinfo_manage.html",{"username":username})
    else:
        return HttpResponse("Sorry,You do not have permission to access the user information management page")


#显示用户信息在用户信息管理页面展示
def userinfo_show(request,username):
    userinfo_all = UserInfo.objects.all()
    userinfo_List = []
    for li in userinfo_all:
        #序列化
        datetimeformat = json.dumps(str(li.createtime))
        createtime = datetimeformat.split('"')[1].split('+')[0]

        if(li.gender):
            gender="男"
        else:
            gender="女"
        # print (createtime)
        userinfo_List.append(
            {"username": li.username, "authority": li.authority, "remark": li.remark, "createtime": createtime,
             "position": li.position,"gender": gender,"id": li.id})
        userinfo_List_len = len(userinfo_List)
    # print (str(eaList))
    json_data_list = {'rows': userinfo_List, 'total': userinfo_List_len}

    userinfoList = json.dumps(json_data_list,cls=CJsonEncoder)
    print (userinfoList)
    return HttpResponse(userinfoList)


#新增成员信息
def add_userinfo(request):
    if request.method == "POST":
        print("add_userinfo POST")

        username = request.POST.get('username')
        authority = request.POST.get('authority')
        remark = request.POST.get('remark')
        position = request.POST.get('position')
        gender = request.POST.get('gender')
        if(gender==u"男"):
            gender = True
        else:
            gender = False

        createtime = datetime.datetime.now()
        print (createtime)
        password = "123456"
        dic = {'username': username,'authority': authority, 'remark':remark,
               'position': position,'gender':gender,'createtime':createtime,'password':password}
        user_count = UserInfo.objects.filter(username=username).count()
        if(user_count>0):
            print ("\"" + username + "\"" + " username repeat")
            return HttpResponse("username repeat")
        else:
            UserInfo.objects.create(**dic)
            return HttpResponse("save")
    else:
        print(" is null_!")
    return render(request, 'AutoFW/workbench_userinfo_manage.html')


#修改成员信息
def edit_userinfo(request,username):
    if request.method == "POST":

        user_id = UserInfo.objects.filter(username=username)[0].id
        #超级用户不允许修改和删除
        user_authority = UserInfo.objects.filter(username=username)[0].authority
        print("edit_userinfo POST")
        username_new = request.POST.get('username')
        authority = request.POST.get('authority')
        remark = request.POST.get('remark')
        position = request.POST.get('position')
        gender = request.POST.get('gender')
        if (gender == u"男"):
            gender = True
        else:
            gender = False
        createtime = datetime.datetime.now()
        dic = {'username': username_new, 'authority': authority, 'remark': remark,
               'position': position, 'gender': gender}

        user_count = UserInfo.objects.filter(username=username_new).count()
        if username_new != username and user_count>0:
            print ("\""+username_new+"\""+" username repeat")
            return HttpResponse("username repeat")
        elif user_authority == "superman":
            print (username+"超级用户不允许修改或删除！")
            return HttpResponse("superman")
        else:
            UserInfo.objects.filter(id=user_id).update(**dic)
            return HttpResponse("save")
    else:
        print(" is null_!")
    return render(request, 'AutoFW/workbench_userinfo_manage.html')


#删除用户信息（超级用户不能删除）
def remove_userinfo(request,username):
    if request.method == "POST":
        print("remove_userinfo")
        print(request.POST.get('id'))
        username = request.POST.get('id')
        user_id = UserInfo.objects.filter(username=username)[0].id
        # 超级用户不允许修改和删除
        user_authority = UserInfo.objects.filter(username=username)[0].authority

        if user_authority == "superman":
            print (str(username)+"超级用户不允许修改或删除！")
            return HttpResponse("superman")
        else:
            UserInfo.objects.filter(id=user_id).delete()
            return HttpResponse("REMOVE")


#重置用户密码（超级用户除外）
def resetPW_userinfo(request,username):
    if request.method == "POST":
        print("resetPW_userinfo")
        user_id = UserInfo.objects.filter(username=username)[0].id
        # 超级用户不允许修改和删除
        user_authority = UserInfo.objects.filter(username=username)[0].authority

        if user_authority == "superman":
            print (str(username)+"超级用户密码不允许重置！")
            return HttpResponse("superman")
        else:
            UserInfo.objects.filter(id=user_id).update(password="123456")
            return HttpResponse("success")


#个人信息管理page
def personal_manage(request,username):
    userinfo = UserInfo.objects.filter(username=username)[0]
    if userinfo.gender:
        gender = "男"
    else:
        gender = "女"
    context = {"username":username,"authority":userinfo.authority,"position":userinfo.position,
                    "gender":gender}
    return render(request,"AutoFW/personal_manage_page.html",context)