#coding=utf-8
import json
import datetime,time
import os
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from .util.execute_script_Popen import execute_script_Popen
from .util.copyFileAndUpdataUtil import copyFile
from .util.send_mail_batch_report import send_mail
from models import *
import MySQLdb
import sys

reload(sys)
sys.setdefaultencoding('utf8')
from .util.Mylogging import mylogging  #自定义异常捕获日志

import logging
log_sys = logging.getLogger("django")  #系统日志
log_scripts = logging.getLogger("scripts")  #执行脚本日志

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

    username_obj = UserInfo.objects.filter(username=user)  #querySet

    if(len(username_obj)>0 and passwd == username_obj[0].password):
        username = username_obj[0].username
        position = username_obj[0].position
        context = {'username': username, 'position': position}
        log_sys.info("["+username+"] 登录成功")
        return render(request, 'AutoFW/easyui_workbench.html', context)
    else:
        log_sys.info("请输入正确的用户名和密码！")
        print ("login_handle:请输入正确的用户名和密码！")
        return render(request, 'AutoFW/login.html')


    # conn = MySQLdb.connect(host='localhost',port=3306,db='autofw',user='root',passwd='*****',charset='utf8')
    # handle = conn.cursor()
    # username = handle.execute("select username from userinfo where username='%s'" % user)
    # username = handle.fetchone()
    # password = handle.execute("select password from userinfo where username='%s'" % user)
    # password = handle.fetchone()
    # print ("username:"+str(username)+"  password:"+str(password))
    # #判断元组是否为空，空为false
    # if(username and password):
    #     # print ("user:"+user+"  passwd:"+passwd)
    #     if(username[0]==user and password[0]==passwd):
    #         username = username[0]
    #         position = UserInfo.objects.filter(username=username)
    #         # print (str(position[0].position))
    #         position = position[0].position
    #         context = {'username':username,'position':position}
    #         return render(request,'AutoFW/easyui_workbench.html',context)
    #     else:
    #         # return HttpResponse("username or passwd1 error")
    #         return render(request, 'AutoFW/login.html')
    # else:
    #     # return HttpResponse("username or passwd error")
    #     return render(request, 'AutoFW/login.html')


def project_manage(request,username):
    log_sys.info("进入项目中心-->项目管理页面")
    content = {"username":username}
    return render(request,'AutoFW/easyui_project_manage.html',content)

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
def Read_all_project(request):
    log_sys.info("查询所有项目")
    obj_all = Project.objects.all()
    eaList = []
    for li in obj_all:
        #序列化
        datetimeformat = json.dumps(str(li.create_time))
        create_time = datetimeformat.split('"')[1].split('+')[0]
        # log_sys.info("datatime类型序列化："+create_time)
        eaList.append(
            {"project_id": li.project_code, "project_name": li.project_name, "creator": li.creator, "create_time": create_time,
             "prioirty": li.PRI,"department": li.department,"id": li.id})
    eaList_len = json.dumps(len(eaList),cls=CJsonEncoder)
    json_data_list = {'rows': eaList, 'total': eaList_len}
    easyList = json.dumps(json_data_list,cls=CJsonEncoder)
    #log_sys.info("项目列表加载：" + str(easyList))
    return HttpResponse(easyList)

# Edit_UserName
def Edit_project(request, id,username):
    print ("username_glp:"+ str(username))
    log_sys.info("编辑更改项目属性")
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        project_name = request.POST.get('project_name')
        creator = username
        create_time = request.POST.get('create_time')
        prioirty = request.POST.get('prioirty')
        department = request.POST.get('department')
        dic = {'project_code': project_id, 'project_name': project_name,
               'creator': creator, 'create_time': create_time,'PRI':prioirty,'department':department};
        log_sys.info("更新项目属性："+str(dic))
        Project.objects.filter(id=id).update(**dic)
        return HttpResponse("Edit_OK")


def income_project(request, project_id,username):
    log_sys.info(str(username)+"进入项目["+str(project_id)+"]")
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

    context = {"project_id":project_id,'list':module_case_count_dir,"username":username}

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

    #获取全局变量
    project_config = Project_Config.objects.filter(project_id=project_id)[0]
    print ("project_attribute project_config:"+str(project_config))
    project_ip = project_config.ip
    project_domain = project_config.domain
    project_port = project_config.port
    project_port_str = str(project_port)
    project_protocol = project_config.protocol

    content = {'create_time':create_times,'creator':creator,
              'department':department,'prioirty':prioirty,'project_name':project_name,
             'project_module_count':project_module_count,'project_case_count':project_case_count,
               'ip':project_ip,'domain':project_domain,'port':project_port_str,'protocol':project_protocol}
    print (content)
    return JsonResponse(content)


#更新配置项目全局变量
def project_globel_config(request,project_id):
    if request.method == "POST":
        print ("project_globel_config post")
        project_ip = request.POST.get('ip')
        project_domain = request.POST.get('domain')
        project_port = request.POST.get('port')
        project_protocol = request.POST.get('protocol')

        if project_port.strip() != '':
            project_port = int(project_port)

        content = {"ip":project_ip,"domain":project_domain,"port":project_port,"protocol":project_protocol}
        print (content)
        #判断项目是否存在配置，不存在就新建，存在就修改
        project_config_count = Project_Config.objects.filter(project_id=project_id).count()
        print ("project_config_count:"+str(project_config_count))

        if project_config_count > 0 and str(project_ip).strip() != '' and str(project_domain).strip() != '' and str(project_port).strip() != '' and str(project_protocol).strip() != '':
            print ("project_globel_config 进入[update]分支！")
            Project_Config.objects.filter(project_id=project_id).update(**content)
            return HttpResponse("update success")
        elif project_config_count == 0:
            print ("project_globel_config 进入[create]分支！")
            content = {"ip": project_ip, "domain": project_domain, "port": project_port,
                       "project_id_id":project_id,"protocol":project_protocol,"bak_field2":"bak2"}
            print (content)
            Project_Config.objects.create(**content)
            return HttpResponse("create success")
        else:
            print ("ip/domain/port 不能为空!")
            return HttpResponse("ip/domain/port 不能为空!")



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
def app_start(request,username):
    # add_save_user
    if request.method == "POST":
        print("POST")
        project_id = request.POST.get('project_id')
        project_name = request.POST.get('project_name')
        creator = username
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
def workon_tabs_api(request,project_id,username):
    log_sys.info(str(username)+"进入接口管理页面 ["+project_id+"]")
    # 获取项目模块list，传递给前端提供给form表单用
    module_name_list = Project_Module.objects.filter(project=project_id).values('module_name')
    # print (module_name_list)
    content = {"project_id":project_id,"module_name_list":module_name_list,"username":username}
    return render(request,'AutoFW/workon_tabs_api_curd.html',content)


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
        # i = 0
        # project_name = project_case_all.values('project_name')[i]['project_name']
        # module_name = project_case_all.values('module_name')[i]['module_name']
        #获取外键指定值 module_name project_name 方法二
        # print (list.module_name.module_name)

        '''case_type 枚举 1:回归测试  2：冒烟测试   3：其他 '''
        if "1" == str(list.case_type):
            case_type = "回归测试"
        elif "2" == str(list.case_type):
            case_type = "冒烟测试"
        elif "3" == str(list.case_type):
            case_type = "其他"
        else:
            print ("case_type 类型错误" + str(list.case_type))

        caseList.append({"case_id":list.case_id,"module_name":list.module_name.module_name,"project_name":list.project_name.project_name,
                         "case_name":list.case_name,"creator":list.creator,"url_path":list.url_path,
                         "method":list.method,"headers":list.headers,"parameter_format":list.parameter_format,"parameter":list.parameter,"expected":list.expected,
                         "description":list.description,"case_type":case_type})
        # i += 1

    caseList_len = len(caseList)
    # print (str(caseList))
    json_data_case_list = {'rows':caseList,'total':caseList_len}
    #序列化
    case_list = json.dumps(json_data_case_list,cls=CJsonEncoder)
    return HttpResponse(case_list)


def API_start(request,project_id,username):
    if request.method == "POST":
        case_id = request.POST.get('case_id')#接口编号
        module_name = request.POST.get('module_name')#模块名称

        #获取项目名，传递给前端
        project_name = Project.objects.filter(project_code=project_id).values('project_name')[0]['project_name']

        case_name = request.POST.get('case_name')#接口名称
        creator = username#创建人
        url_path = request.POST.get('url_path')
        method = request.POST.get('method')
        headers = request.POST.get('headers')
        parameter_format = request.POST.get('parameter_format')
        parameter = request.POST.get('parameter')
        expected = request.POST.get('expected')
        description = request.POST.get('description')
        case_type = request.POST.get('case_type')
        '''case_type 枚举 1:回归测试  2：冒烟测试   3：其他 '''
        if "回归测试" == str(case_type):
            case_type = 1
        elif "冒烟测试" == str(case_type):
            case_type = 2
        elif "其他" == str(case_type):
            case_type = 3
        else:
            print ("case_type 类型错误"+str(case_type))

        # module_name_id是外键 本应是module_name    project_name_id是外键 本应是project_name
        dic = {'case_id': case_id,'module_name_id': module_name, 'project_name_id':project_name,
               'case_name': case_name,'creator':creator,'url_path':url_path,'method':method,'headers':headers,
               'parameter_format':parameter_format,'parameter':parameter,'expected':expected,'description':description,
               'case_type':case_type}

        Project_Case.objects.create(**dic)

        log_sys.info(str(username) + "添加API用例 ["+str(case_name)+"] 属于项目：[" + project_id + "]")

        return HttpResponse("save")
    else:
        print(" is null_!")
    return render(request, 'AutoFW/workon_project.html')


def editAPI(request,project_id,username):
    if request.method == "POST":
        print ("editAPI submit")
        case_id = request.POST.get('case_id')
        case_name = request.POST.get('case_name')
        url_path = request.POST.get('url_path')
        method = request.POST.get('method')
        headers = request.POST.get('headers')
        parameter_format = request.POST.get('parameter_format')
        parameter = request.POST.get('parameter')
        expected = request.POST.get('expected')
        module_name = request.POST.get('module_name')
        description = request.POST.get('description')
        case_type = request.POST.get('case_type')

        '''case_type 枚举 1:回归测试  2：冒烟测试   3：其他 '''
        if "回归测试" == str(case_type):
            case_type = 1
        elif "冒烟测试" == str(case_type):
            case_type = 2
        elif "其他" == str(case_type):
            case_type = 3
        else:
            print ("case_type 类型错误" + str(case_type))

        # print (module_name)
        creator = username
        print (headers)
        project_name = Project.objects.filter(project_code=project_id).values('project_name')[0]['project_name']

        dic = {'case_id': case_id, 'case_name': case_name,
               'url_path': url_path, 'method': method,'headers':headers,'parameter_format':parameter_format,
               'parameter': parameter, 'expected': expected,
               'module_name': module_name, 'project_name': project_name,
               'description': description,"case_type":case_type};
        print(str(dic))
        project_case_obj = Project_Case.objects.filter(case_id=case_id)
        if len(project_case_obj)==1:
            Project_Case.objects.filter(case_id=case_id).update(**dic)#case_id 不让更改
            return HttpResponse("save")
        else:
            return HttpResponse("case_id can't change.")


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
    print ("personal_manage")
    emp_info_obj = Emp_Info.objects.filter(user_id=username)

    print ("emp_info:"+str(emp_info_obj))

    if emp_info_obj:
        # print ("if fenzhi")
        emp_info = Emp_Info.objects.filter(user_id=username)[0]

        name = Emp_Info.objects.filter(user_id=username)[0].name

        birthday = str(emp_info.birthday).split(' ')[0]

        content = {"username": username,"name":name, "birthday": birthday, "phone_id": emp_info.phone_id,
               "position": emp_info.position, "email": emp_info.email, "job_number": emp_info.job_number}
        print(content)
        return render(request,"AutoFW/personal_manage_page.html",content)
    else:
        # print ("else fenzhi")
        content = {"username": username, "name": "", "birthday": "", "phone_id": "",
                   "position": "", "email": "", "job_number": ""}
        return render(request, "AutoFW/personal_manage_page.html", content)

#个人信息修改页面 更新个人信息
def update_emp_info(request,username):
    if request.method == "POST":
        print ("update_emp_info POST")
        name = request.POST.get("name")
        birthday = request.POST.get("birthday")
        print (birthday)
        birthday = str(birthday)+" 00:00:00"
        birthday_fmt = datetime.datetime.strptime(birthday, "%Y-%m-%d %H:%M:%S").date()
        phone_id = request.POST.get("phone_id")
        position = request.POST.get("position")
        email = request.POST.get("email")
        job_number = request.POST.get("job_number")
        job_number_fmi = int(job_number)

        content = {"name":name,"birthday":birthday_fmt,"phone_id":phone_id,
                   "position":position,"email":email,"job_number":job_number_fmi}
        print (content)

        #判断是否存在该成员信息
        emp_info_obj = Emp_Info.objects.filter(user_id=username)
        if emp_info_obj:
            Emp_Info.objects.filter(user_id=username).update(**content)
        else:
            content = {"user_id_id":username,"name": name, "birthday": birthday_fmt, "phone_id": phone_id,
                       "position": position, "email": email, "job_number": job_number_fmi,"salery":0,
                       "work_year":0,"remark":"tester","other":"other"}
            Emp_Info.objects.create(**content)

        #重新构造时间数据格式给前端使用，否则出现系统默认格式
        emp_info = Emp_Info.objects.filter(user_id=username)[0]
        birthday = str(emp_info.birthday).split(' ')[0]
        content = {"username":username,"name": name, "birthday": birthday, "phone_id": phone_id,
                   "position": position, "email": email, "job_number": job_number_fmi}
        return render(request,"AutoFW/personal_manage_page.html",content)


#修改个人密码
def change_pw(request,username):
    print ("change_pw")
    if request.method == "POST":
        post = request.POST.get
        password = UserInfo.objects.filter(username=username)[0].password
        print (password)
        old_pw = post("old_pw")
        new_pw = post("new_pw")
        confirm_pw = post("confirm_pw")
        #判断输入的旧密码是否正确
        if old_pw == password:
            #判断输入的两次密码是否相同
            if new_pw == confirm_pw:
                content = {"password":new_pw}
                UserInfo.objects.filter(username=username).update(**content)
                return personal_manage(request,username)
            else:
                print ("The two input password is incorrect")
        else:
            print ("old password error!")
        return personal_manage(request, username)


#测试用例过滤和生成测试用例
def test_case_genirate_page(request,username):
    print ("test_case_genirate_page")
    #项目名称ValuesQuerySet
    project_qs = Project.objects.values("project_name")
    #获取成员姓名
    creator = Emp_Info.objects.values("name")

    print (creator)
    content = {"project_name_list":project_qs,"creator_list":creator}

    return render(request,"AutoFW/test_case_genirate_page.html",content)


#select下拉框ajax出发事件 （根据项目名称更新模块）
def select_load_module(request,project_name):
    print ("select_load_module")
    project_code = Project.objects.filter(project_name=project_name)[0].project_code
    print (project_code)

    module_name = Project_Module.objects.filter(project=project_code).values("module_name")
    module_name_list = []
    #将module_name存放到list中
    for i in module_name:
        module_name_list.append(i["module_name"])
    # print (module_name_list)

    data = {"status":"success","module_name":module_name_list}
    print (data)
    return JsonResponse(data)


#根据提交条件查询测试用例
def search_case(request):
    print ("search_case")
    get = request.GET.get
    project_name = get("project_name")
    #unicode转str
    project_name = project_name.encode("utf8")
    creator_name = get("creator_name")
    # unicode转str
    creator_name = creator_name.encode("utf8")
    project_module = get("project_module")
    case_status = get("case_status")
    case_name = get("case_name")
    print (project_name)
    print (creator_name)
    print (project_module)
    print (str(case_status))
    print (str(case_name))
    #获取全局配置IP/PORT变量
    project_obj = Project.objects.filter(project_name=project_name)[0]
    # print (project_obj)
    project_id = project_obj.project_code
    # print (project_id)
    prject_obj = Project_Config.objects.filter(project_id=project_id)[0]
    prject_config_ip = prject_obj.ip
    prject_config_port = prject_obj.port
    #存放给前端table用的case数据
    case_obj_list = []

    #创建者/用例状态/用例名 为空时查询分支
    if creator_name == "" and str(case_status) == "" and str(case_name) == "":
        print ("创建者/用例状态/用例名 为空时查询分支")
        case_obj = Project_Case.objects.filter(project_name=project_name,module_name=project_module)
        for list in case_obj:
            case_obj_dict = {"case_id":list.case_id,"case_name":list.case_name,"project_name":list.project_name_id,"module_name":list.module_name_id,
                             "url_path":list.url_path,"method":list.method,"headers":list.headers,"ip":prject_config_ip,"parameter_format":list.parameter_format,"parameter":list.parameter,
                             "expected":list.expected,"port":prject_config_port,"creator":list.creator,"case_status":list.description}
            case_obj_list.append(case_obj_dict)
        # print (case_obj_list)
        content = {"status": "success", "case_list": case_obj_list}
        print (content)
        return JsonResponse(content)
    # 创建者/用例状态 为空时查询分支
    elif creator_name == "" and str(case_status) == "":
        print ("创建者/用例状态 为空时查询分支")
        #case_name支持模糊查询
        case_obj = Project_Case.objects.filter(project_name=project_name,
                                               module_name=project_module,case_name__contains=case_name)
        for list in case_obj:
            case_obj_dict = {"case_id":list.case_id,"case_name": list.case_name, "project_name": list.project_name_id,"module_name": list.module_name_id,
                             "url_path": list.url_path, "method": list.method,"headers":list.headers, "ip": prject_config_ip,"parameter_format":list.parameter_format,"parameter": list.parameter,
                             "expected": list.expected, "port": prject_config_port,"creator":list.creator,"case_status":list.description}
            case_obj_list.append(case_obj_dict)
        # print (case_obj_list)
        content = {"status": "success", "case_list": case_obj_list}
        print (content)
        return JsonResponse(content)
    # 创建者/用例名称 为空时查询分支
    elif creator_name == "" and str(case_name) == "":
        print ("创建者/用例名称 为空时查询分支")
        case_obj = Project_Case.objects.filter(project_name=project_name,
                                               module_name=project_module,description=case_status)
        for list in case_obj:
            case_obj_dict = {"case_id":list.case_id,"case_name": list.case_name, "project_name": list.project_name_id,"module_name": list.module_name_id,
                             "url_path": list.url_path, "method": list.method,"headers":list.headers, "ip": prject_config_ip,"parameter_format":list.parameter_format,"parameter": list.parameter,
                             "expected": list.expected, "port": prject_config_port,"creator":list.creator,"case_status":list.description}
            case_obj_list.append(case_obj_dict)
        # print (case_obj_list)
        content = {"status": "success", "case_list": case_obj_list}
        print (content)
        return JsonResponse(content)
    # 用例名称/用例状态 为空时查询分支
    elif str(case_status) == "" and str(case_name) == "":
        print ("用例名称/用例状态 为空时查询分支")
        #获取用户id
        creator_n = Emp_Info.objects.filter(name=creator_name)[0].user_id_id
        print (creator_n)
        case_obj = Project_Case.objects.filter(project_name=project_name,
                                               module_name=project_module,creator=creator_n)
        # print (case_obj)
        for list in case_obj:
            case_obj_dict = {"case_id":list.case_id,"case_name": list.case_name, "project_name": list.project_name_id,"module_name": list.module_name_id,
                             "url_path": list.url_path, "method": list.method,"headers":list.headers, "ip": prject_config_ip,"parameter_format":list.parameter_format,"parameter": list.parameter,
                             "expected": list.expected, "port": prject_config_port,"creator":list.creator,"case_status":list.description}
            case_obj_list.append(case_obj_dict)
        # print (case_obj_list)
        content = {"status": "success", "case_list": case_obj_list}
        print (content)
        return JsonResponse(content)
    # 创建者 为空时查询分支
    elif creator_name == "":
        print ("创建者 为空时查询分支")
        # case_name支持模糊查询
        case_obj = Project_Case.objects.filter(project_name=project_name,module_name=project_module,
                                               case_name__contains=case_name,description=case_status)
        # print (case_obj)
        for list in case_obj:
            case_obj_dict = {"case_id":list.case_id,"case_name": list.case_name, "project_name": list.project_name_id,
                             "module_name": list.module_name_id,
                             "url_path": list.url_path, "method": list.method,"headers":list.headers, "ip": prject_config_ip,
                             "parameter_format":list.parameter_format,"parameter": list.parameter,
                             "expected": list.expected, "port": prject_config_port, "creator": list.creator,
                             "case_status": list.description}
            case_obj_list.append(case_obj_dict)
        # print (case_obj_list)
        content = {"status": "success", "case_list": case_obj_list}
        print (content)
        return JsonResponse(content)
    # 用例状态 为空时查询分支
    elif case_status == "":
        print ("用例状态 为空时查询分支")
        # 获取用户id
        creator_n = Emp_Info.objects.filter(name=creator_name)[0].user_id_id

        case_obj = Project_Case.objects.filter(project_name=project_name,module_name=project_module,
                                               case_name__contains=case_name,creator=creator_n)
        for list in case_obj:
            case_obj_dict = {"case_id":list.case_id,"case_name": list.case_name, "project_name": list.project_name_id,
                             "module_name": list.module_name_id,
                             "url_path": list.url_path, "method": list.method,"headers":list.headers, "ip": prject_config_ip,
                             "parameter_format":list.parameter_format,"parameter": list.parameter,
                             "expected": list.expected, "port": prject_config_port, "creator": list.creator,
                             "case_status": list.description}
            case_obj_list.append(case_obj_dict)
        # print (case_obj_list)
        content = {"status": "success", "case_list": case_obj_list}
        print (content)
        return JsonResponse(content)
    # 用例名称 为空时查询分支
    elif case_name == "":
        print ("用例名称 为空时查询分支")
        # 获取用户id
        creator_n = Emp_Info.objects.filter(name=creator_name)[0].user_id_id
        case_obj = Project_Case.objects.filter(project_name=project_name,module_name=project_module,
                                               description=case_status,creator=creator_n)
        for list in case_obj:
            case_obj_dict = {"case_id":list.case_id,"case_name": list.case_name, "project_name": list.project_name_id,
                             "module_name": list.module_name_id,
                             "url_path": list.url_path, "method": list.method,"headers":list.headers, "ip": prject_config_ip,
                             "parameter_format":list.parameter_format,"parameter": list.parameter,
                             "expected": list.expected, "port": prject_config_port, "creator": list.creator,
                             "case_status": list.description}
            case_obj_list.append(case_obj_dict)
        # print (case_obj_list)
        content = {"status": "success", "case_list": case_obj_list}
        print (content)
        return JsonResponse(content)
    else:
        print ("所有查询条件不为空时查询分支")
        # 获取用户id
        creator_n = Emp_Info.objects.filter(name=creator_name)[0].user_id_id
        case_obj = Project_Case.objects.filter(project_name=project_name, module_name=project_module,
                                               description=case_status, creator=creator_n,case_name__contains=case_name)
        for list in case_obj:
            case_obj_dict = {"case_id":list.case_id,"case_name": list.case_name, "project_name": list.project_name_id,
                             "module_name": list.module_name_id,
                             "url_path": list.url_path, "method": list.method,"headers":list.headers, "ip": prject_config_ip,
                             "parameter_format":list.parameter_format,"parameter": list.parameter,
                             "expected": list.expected, "port": prject_config_port, "creator": list.creator,
                             "case_status": list.description}
            case_obj_list.append(case_obj_dict)
        # print (case_obj_list)
        content = {"status": "success", "case_list": case_obj_list}
        print (content)
        return JsonResponse(content)


#生成测试脚本（全选模式/单选）
def chose_all_genritor_test_script(request):
    print ("chose_all_genritor_test_script")
    case_id = request.GET.get("case_id_json")
    # case_name = case_name.encode("utf-8")
    case_id_list = str(case_id).split(',')

    #移除空列元素
    case_id_list.remove('')

    '''sourceFile/targetFile相对路径'''
    sourceFile = "script/HTTP_API_case_templates/"
    targetFile = "script/genirtor_script/"

    # print (os.getcwd()) #/home/fzyzgong/project/AutoFWOG

    parent_path = os.getcwd() + "/AutoFW/" + targetFile
    print (parent_path)

    for list in case_id_list:
        print (list)
        project_case_obj = Project_Case.objects.filter(case_id=list)[0]
        #project_name ForigenKye
        project_name = project_case_obj.project_name_id
        project_obj = Project.objects.filter(project_name=project_name)[0]
        project_id = project_obj.project_code

        project_config_obj = Project_Config.objects.filter(project_id=project_id)[0]

        ip = str(project_config_obj.ip)
        domain = project_config_obj.domain.replace(' ','')  #去除空格
        protocol = project_config_obj.protocol.replace(' ','')  #去除空格
        url = str(project_case_obj.url_path).replace(' ','')  #去除空格
        method = str(project_case_obj.method).replace(' ', '')  # 去除空格

        #headers 和 param 可以为空 GET/POST 不同时分支
        headers = str(project_case_obj.headers)
        param_format = str(project_case_obj.parameter_format)
        param = str(project_case_obj.parameter)
        expected = str(project_case_obj.expected)

        #字符串转字典
        # headers = eval(headers_tmp)
        # param = eval(param_tmp)
        # expected = eval(expected_tmp)
        print (headers,param,expected)

        fileName = str(project_case_obj.case_name) + "-" + str(datetime.datetime.now().year) + \
            "_" + str(datetime.datetime.now().month) + "_" + str(datetime.datetime.now().day) + \
            "_" + str(datetime.datetime.now().hour) + "_" + str(datetime.datetime.now().minute)+ \
            "_" + str(datetime.datetime.now().second) + ".py"

        # '''复制重命名'''
        # fileName = "1234.py"
        # ip = "http://www.sojson.com"
        # url = "/open/api/weather/json.shtml"
        #
        # '''以字符串格式传给复制替换，否则遇中文转码'''
        # param = '{"city": "北京"}'
        # expected = '{"message": "Success !"}'
        #

        copyFile(sourceFile, targetFile, fileName,protocol,method, domain, url,headers,param_format, param, expected)
        create_time = fileName.split('-')[1].split('.')[0]
        print (create_time)
        dict = {"script_name":fileName,"script_path":parent_path+fileName,"script_case_name":project_case_obj.case_name,
                "create_time":create_time,"script_module_name_id":project_case_obj.module_name_id,
                "script_status":"NONE","script_project_name_id":project_name,"remark":"remark","script_case_id_id":list}
        print (dict)
        Script_Info.objects.create(**dict)

    content = {"status":"genirtor_script_success","targetDir":parent_path}
    return JsonResponse(content)


#进入执行脚本页面
def execute_test_script_page(request,username):
    print ("execute_test_script_page")
    # 项目名称ValuesQuerySet
    project_qs = Project.objects.values("project_name")

    content = {"project_name_list": project_qs,"username":username}
    return render(request,"AutoFW/execute_test_script_page.html",content)


#查询脚本
def search_script(request):
    print ("search_script")
    get = request.GET.get
    project_name = get("project_name")
    # unicode转str
    project_name = project_name.encode("utf8")
    create_time = get("create_time") #2017-11-20 11:50:02
    #转换格式
    create_time_w = str(create_time).split(' ')[0].replace("-","_")
    # unicode转str
    create_time = create_time.encode("utf8")
    project_module = get("project_module")
    script_status = get("script_status")
    script_name = get("script_name")
    print (project_name)
    print (create_time_w)
    print (project_module)
    print (script_status)
    print (script_name)
    # 获取全局配置IP/PORT变量
    # script_info = Script_Info.objects.filter(script_module_name=project_module)[0]
    # print (project_obj)


    # 存放给前端table用的case数据
    script_obj_list = []

    # # 创建时间/用例状态/脚本名称 为空时查询分支
    if create_time == "" and str(script_status) == "" and str(script_name) == "":
        print ("创建时间/脚本状态/脚本名称 为空时查询分支")
        script_obj = Script_Info.objects.filter(script_project_name=project_name, script_module_name=project_module)
        for list in script_obj:
            create_times = list.create_time #2017_11_20_10_4_54
            #转换格式 2017_11_20
            create_time_h = str(create_times).rsplit('_',3)[0].replace("_","-")

            script_obj_dict = {"script_name": list.script_name, "script_path": list.script_path,
                             "script_case_name": list.script_case_name,
                             "create_time": create_time_h, "script_module_name": list.script_module_name_id,
                               "script_status":list.script_status,"script_project_name":list.script_project_name_id}
            script_obj_list.append(script_obj_dict)
        # print (case_obj_list)
        content = {"status": "success", "script_list": script_obj_list}
        print (content)
        return JsonResponse(content)
    # 创建时间/脚本状态 为空时查询分支
    elif create_time == "" and str(script_status) == "":
        print ("创建时间/脚本状态 为空时查询分支")
        # script_name支持模糊查询
        script_obj = Script_Info.objects.filter(script_project_name=project_name,
                                               script_module_name=project_module, script_name__contains=script_name)
        for list in script_obj:
            create_times = list.create_time  # 2017_11_20_10_4_54
            # 转换格式 2017_11_20
            create_time_h = str(create_times).rsplit('_', 3)[0].replace("_", "-")
            script_obj_dict = {"script_name": list.script_name, "script_path": list.script_path,
                             "script_case_name": list.script_case_name,
                             "create_time": create_time_h, "script_module_name": list.script_module_name_id,
                               "script_status":list.script_status,"script_project_name":list.script_project_name_id}
            script_obj_list.append(script_obj_dict)
        # print (case_obj_list)
        content = {"status": "success", "script_list": script_obj_list}
        print (content)
        return JsonResponse(content)
    # 创建时间/脚本名称 为空时查询分支
    elif create_time == "" and str(script_name) == "":
        print ("创建时间/脚本名称 为空时查询分支")
        script_obj = Script_Info.objects.filter(script_project_name=project_name,
                                               script_module_name=project_module, script_status=script_status)
        for list in script_obj:
            create_times = list.create_time  # 2017_11_20_10_4_54
            # 转换格式 2017_11_20
            create_time_h = str(create_times).rsplit('_', 3)[0].replace("_", "-")
            script_obj_dict = {"script_name": list.script_name, "script_path": list.script_path,
                               "script_case_name": list.script_case_name,
                               "create_time": create_time_h, "script_module_name": list.script_module_name_id,
                               "script_status": list.script_status, "script_project_name": list.script_project_name_id}
            script_obj_list.append(script_obj_dict)
        # print (case_obj_list)
        content = {"status": "success", "script_list": script_obj_list}
        print (content)
        return JsonResponse(content)
    # 脚本状态/脚本名称 为空时查询分支
    elif str(script_status) == "" and str(script_name) == "":
        print ("脚本状态/脚本名称 为空时查询分支")
        # 2017-11-20 11:50:02 转成 2017_11_20_11_50_02
        create_time = str(create_time).split(' ')[0].replace("-","_")
        # print ("create_time:转成"+create_time)
        script_obj = Script_Info.objects.filter(script_project_name=project_name,
                                               script_module_name=project_module, create_time__contains=create_time)

        for list in script_obj:
            script_obj_dict = {"script_name": list.script_name, "script_path": list.script_path,
                               "script_case_name": list.script_case_name,
                               "create_time": create_time, "script_module_name": list.script_module_name_id,
                               "script_status": list.script_status, "script_project_name": list.script_project_name_id}
            script_obj_list.append(script_obj_dict)

        content = {"status": "success", "script_list": script_obj_list}
        print (content)
        return JsonResponse(content)
    # 创建时间 为空时查询分支
    elif create_time == "":
        print ("创建时间 为空时查询分支")
        # script_name支持模糊查询
        script_obj = Script_Info.objects.filter(script_project_name=project_name, script_module_name=project_module,
                                                script_name__contains=script_name, script_status=script_status)
        # print (case_obj)
        for list in script_obj:
            create_times = list.create_time  # 2017_11_20_10_4_54
            # 转换格式 2017_11_20
            create_time_h = str(create_times).rsplit('_', 3)[0].replace("_", "-")
            script_obj_dict = {"script_name": list.script_name, "script_path": list.script_path,
                               "script_case_name": list.script_case_name,
                               "create_time": create_time_h, "script_module_name": list.script_module_name_id,
                               "script_status": list.script_status, "script_project_name": list.script_project_name_id}
            script_obj_list.append(script_obj_dict)

        content = {"status": "success", "script_list": script_obj_list}
        print (content)
        return JsonResponse(content)
    # 脚本状态 为空时查询分支
    elif script_status == "":
        print ("脚本状态 为空时查询分支")
        # 2017-11-20 11:50:02 转成 2017_11_20_11_50_02
        create_time = str(create_time).split(' ')[0].replace("-", "_")
        # script_name支持模糊查询
        script_obj = Script_Info.objects.filter(script_project_name=project_name, script_module_name=project_module,
                                                script_name__contains=script_name, create_time__contains=create_time)

        for list in script_obj:
            script_obj_dict = {"script_name": list.script_name, "script_path": list.script_path,
                               "script_case_name": list.script_case_name,
                               "create_time": create_time, "script_module_name": list.script_module_name_id,
                               "script_status": list.script_status, "script_project_name": list.script_project_name_id}
            script_obj_list.append(script_obj_dict)

        content = {"status": "success", "script_list": script_obj_list}
        print (content)
        return JsonResponse(content)
    # 脚本名称 为空时查询分支
    elif script_name == "":
        print ("脚本名称 为空时查询分支")
        # 2017-11-20 11:50:02 转成 2017_11_20_11_50_02
        create_time = str(create_time).split(' ')[0].replace("-", "_")
        # create_time支持模糊查询
        script_obj = Script_Info.objects.filter(script_project_name=project_name, script_module_name=project_module,
                                                script_status=script_status, create_time__contains=create_time)

        for list in script_obj:
            script_obj_dict = {"script_name": list.script_name, "script_path": list.script_path,
                               "script_case_name": list.script_case_name,
                               "create_time": create_time, "script_module_name": list.script_module_name_id,
                               "script_status": list.script_status, "script_project_name": list.script_project_name_id}
            script_obj_list.append(script_obj_dict)

        content = {"status": "success", "script_list": script_obj_list}
        print (content)
        return JsonResponse(content)
    else:
        print ("所有查询条件不为空时查询分支")
        # 2017-11-20 11:50:02 转成 2017_11_20_11_50_02
        create_time = str(create_time).split(' ')[0].replace("-", "_")

        script_obj = Script_Info.objects.filter(script_project_name=project_name, script_module_name=project_module,
                                                script_status=script_status, create_time__contains=create_time,
                                                script_name__contains=script_name)
        for list in script_obj:
            script_obj_dict = {"script_name": list.script_name, "script_path": list.script_path,
                               "script_case_name": list.script_case_name,
                               "create_time": create_time, "script_module_name": list.script_module_name_id,
                               "script_status": list.script_status, "script_project_name": list.script_project_name_id}
            script_obj_list.append(script_obj_dict)

        content = {"status": "success", "script_list": script_obj_list}
        print (content)
        return JsonResponse(content)

#执行脚本
def execute_test_script(request):
    print ("execute_test_script")
    if request.method == "GET":
        passCount = 0
        failCount = 0
        skipCount = 0
        script_name = request.GET.get("script_name_json")#获取脚本所在表单索引
        report_name = request.GET.get("result_name")#执行该批次的测试报告名称
        execute_man = request.GET.get("username")#获取执行人的姓名
        send_email_flag = request.GET.get("send_email_flag")#获取是否发送邮件标识[只发送给执行用例人]

        script_name_list = str(script_name).split(',')
        # 移除空列元素
        script_name_list.remove('')
        # print (script_name_list)
        report_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")#报告ID 唯一值 根据当前时间生成
        API_total = len(script_name_list)#本次执行的总API数
        execute_time = datetime.datetime.now()#执行当前时间

        dict_report_id = {"report_id": report_id, "report_name": report_name, "API_total": str(API_total),
                        "pass_total": str(passCount), "fail_total": str(failCount), "skip_total": str(skipCount),
                        "execute_man": str(execute_man),
                        "execute_time": execute_time, "bak1": "bak", "bak2": "bak"}

        Batch_Report.objects.create(**dict_report_id)


        for list in script_name_list:
            API_name = str(list.split('/')[-1]) #接口用例名
            print("API_name:%s"%API_name)
            script_info_obj = Script_Info.objects.filter(script_name=list)[0]
            script_path = str(script_info_obj.script_path)

            # project_case_name = script_info_obj.script_case_name
            script_case_id = script_info_obj.script_case_id

            # print (script_path)
            rs = execute_script_Popen(script_path,0.1) #脚本路径/休眠时间 (当前测试接口需要等待3秒才能再次访问)
            print(rs)

            passCount,failCount,skipCount = execute_script_result_analysis_fun(rs, script_path, report_id, script_case_id, API_name,passCount,failCount,skipCount)


        #     try:
        #         result =rs.split('AutoFW test reslut:')[1].split('\'')[0]
        #         # result = str(result).replace("\n","")
        #         print ("---------")
        #         print (script_path+'：执行结果'+result)
        #         print ("---------")
        #         # 修改脚本实例表 脚本状态字段标识
        #         if result:
        #             rs = rs.split('AutoFW test reslut:')[1]
        #
        #             if "PASS" == result:
        #                 # dict = {"script_status":"PASS"}
        #                 dict = "PASS"
        #                 time_consuming = rs.split('time_consuming:')[1].split(']')[0]
        #                 # log_scripts.info(list + ":PASS:" + " pass message [" + rs.split('PASS')[1] + "]")#响应信息都打印
        #                 log_scripts.info(list + ":PASS:[time_consuming:"+time_consuming+"]{ response : \'resultCode" + rs.split('resultCode')[1][1:4]+'\''+" }")#只打印成功关键字段
        #
        #                 execute_script_log = str(API_name)+":<PASS> [time_consuming:"+time_consuming+"]{ response : \'resultCode" + rs.split('resultCode')[1][1:4]+'\''+" }"
        #
        #                 # 写入Execute_Script_Log表
        #                 dic ={"log_report_id_id":report_id,"log_api_name":API_name,"log_execute_script":execute_script_log,"status":"pass","bak1":"bak"}
        #                 Execute_Script_Log.objects.create(**dic)
        #                 passCount += 1
        #             elif "FAILED" == result:
        #                 # dict = {"script_status": "FAILED"}
        #                 dict = "FAILED"
        #                 log_scripts.error(list + ":FAILED:" + " error message [" + rs.split('FAILED')[1] + "]")
        #
        #                 execute_script_log = str(API_name)+":<FAIL> " + " error message 服务器返回错误：[" + rs.split('FAILED')[1][1:1500] + "]" #设这1-1500为了防止存储字段超过长度
        #                 # 写入Execute_Script_Log表
        #                 dic = {"log_report_id_id": report_id, "log_api_name": API_name,
        #                        "log_execute_script": execute_script_log, "status": "fail", "bak1": "bak"}
        #                 Execute_Script_Log.objects.create(**dic)
        #                 failCount += 1
        #         else:
        #             # dict = {"script_status": "NONE"}
        #             dict = "NONE"
        #             execute_script_log = str(API_name) + ":<FAILED> " + " error message [脚本运行出错]"
        #             # 写入Execute_Script_Log表
        #             dic = {"log_report_id_id": report_id, "log_api_name": API_name,
        #                    "log_execute_script": execute_script_log, "status": "skip", "bak1": "bak"}
        #             Execute_Script_Log.objects.create(**dic)
        #             skipCount += 1
        #     except IndexError,e:
        #         # dict = {"script_status": "NONE"}
        #         dict = "NONE"
        #         mylogging("["+str(list)+"] :"+"未获取脚本执行状态，脚本执行失败")
        #         log_scripts.error(list + ":FAILED:" + " error message [ 未获取脚本执行状态，脚本执行失败 ] \r"+rs)
        #
        #         execute_script_log = str(API_name) + ":<FAILED> " + " error message [脚本运行异常:请查看error.log] \r"+rs
        #         # 写入Execute_Script_Log表
        #         dic = {"log_report_id_id": report_id, "log_api_name": str(API_name),
        #                "log_execute_script": execute_script_log, "status": "skip", "bak1": "bak"}
        #         Execute_Script_Log.objects.create(**dic)
        #         skipCount += 1
        #     # except AttributeError,e:
        #     #     dict = {"script_status": "NONE"}
        #     #     mylogging("[" + str(list) + "] :" + "index error,未获取脚本执行状态，脚本执行失败"+e.args)
        #     #     log_scripts.error(list + ":FAILED:" + " error message [ AttributeError ]"+e.args)
        #     Script_Info.objects.filter(script_name=list).update(script_status=dict)
        #     Project_Case.objects.filter(case_name=project_case_name).update(description=dict) #description 为用例执行状态
        content = {"status": "execute_script_success"}
        # 报告名 执行者 api总数 执行时间 执行报告ID
        print("result_name=%s execute_name=%s api_total=%s"
              " execute_time=%s report_id=%s" % (report_name, execute_man, str(API_total), execute_time, report_id))
        # pass fail skip
        # print("passCount=%s failCount=%s skipCount=%s"%(passCount,failCount,skipCount))

        dict_execute = {"report_id":report_id,"report_name":report_name,"API_total":str(API_total),"pass_total":str(passCount),"fail_total":str(failCount),"skip_total":str(skipCount),"execute_man":str(execute_man),
                        "execute_time":execute_time,"bak1":"bak","bak2":"bak"}

        Batch_Report.objects.filter(report_id=report_id).update(**dict_execute)

        #-------start-------发送测试报告邮件---------------------
        execute_time = execute_time.strftime("%Y%m%d%H%M%S")
        emp_obj_list = Emp_Info.objects.filter(user_id_id=execute_man) #主键，只有一条数据
        if send_email_flag == "yes":
            if emp_obj_list.exists():
                email_adr_list = []
                for list in emp_obj_list:
                    emails = list.email
                    email_adr_list.append(emails)
                send_mail(report_name,execute_man,execute_time,str(API_total),str(passCount),str(failCount),str(skipCount),email_adr_list)
            else:
                print ("该用户没有邮箱信息！")
                content = {"status": "email_send_fail"}
        # -------end-------发送测试报告邮件---------------------
        return JsonResponse(content)

#删除脚本
def delete_test_script(request):
    print ("delete_test_script")
    if request.method == "GET":
        script_name = request.GET.get("script_name_json")
        script_name_list = str(script_name).split(',')
        # 移除空列元素
        script_name_list.remove('')
        for list in script_name_list:
            script_info_obj = Script_Info.objects.filter(script_name=list)[0]
            script_path = str(script_info_obj.script_path)
            #删除物理存储文件
            os.remove(script_path)
            print ("Delete File: " + script_path)
            script_obj = Script_Info.objects.get(script_name=list)
            #删除数据库存储数据
            script_obj.delete()
        content = {"status": "delete_script_success"}
        return JsonResponse(content)

#进入日志模块
def script_log_page(request,username):
    print ("script_log_page")

    file = os.path.join(os.path.dirname(__file__),"log/script.log")

    with open(file,'r',buffering=1024) as f:
        content = f.read()

    return render(request,"AutoFW/script_log_page.html",{"content":content})

#删除脚本日志
def delete_script_log(request):
    print ("delete_script_log")

    file = os.path.join(os.path.dirname(__file__), "log/script.log")
    with open(file, 'r+', buffering=1024) as f:
        f.truncate()
        content = f.read()

    return render(request,"AutoFW/script_log_page.html",{"content":content})


#进入日志模块
def error_log_page(request,username):
    print ("error_log_page")

    file = os.path.join(os.path.dirname(__file__),"log/error.log")

    with open(file,'r',buffering=1024) as f:
        content = f.read()

    return render(request,"AutoFW/error_log_page.html",{"content":content})


def delete_error_log(request):
    print ("delete_log_page")

    file = os.path.join(os.path.dirname(__file__), "log/error.log")
    with open(file, 'r+', buffering=1024) as f:
        f.truncate()
        content = f.read()

    return render(request,"AutoFW/error_log_page.html",{"content":content})


def report_page(request,username):
    print ("report_page")
    execute_man = UserInfo.objects.values("username")

    content = {"execute_man_list": execute_man, "username": username}
    return render(request, "AutoFW/report_page.html", content)



def search_report_list(request):
    print ("search_report_list")
    if request.method == "GET":
        report_name = request.GET.get("report_name")
        execute_man = request.GET.get("execute_man")

        # 存放给前端table用的报告数据
        report_obj_list = []
        if(execute_man == "" and report_name == ""):
            content = {"status": "search_report_list failed ,gei me a condition"}
            return JsonResponse(content)
        elif execute_man == "":
            batch_report_obj = Batch_Report.objects.filter(report_name__contains=report_name)

            for list in batch_report_obj:
                execute_time_tmp = list.execute_time  # 该批次执行时间点
                execute_time = execute_time_tmp.strftime('%Y-%m-%d')  # 将datatime转成str
                data = {
                    "report_id": list.report_id, "API_total": list.API_total,
                    "pass_total": list.pass_total, "fail_total": list.fail_total,
                    "skip_total": list.skip_total, "execute_man": list.execute_man,
                    "execute_time":execute_time,"report_name":list.report_name
                }
                report_obj_list.append(data)

            content = {"status": "success", "report_list": report_obj_list}
            print (content)
            return JsonResponse(content)
            # report_id = batch_report_obj.report_id #报告ID
            # API_total = batch_report_obj.API_total #该批次测试用例总数
            # pass_total = batch_report_obj.pass_total #该批次测试通过总数
            # fail_total = batch_report_obj.fail_total #该批次测试失败总数
            # skip_total = batch_report_obj.skip_total #该批次测试跳过总数
            # execute_man = batch_report_obj.execute_man #该批次测试执行人
            # execute_time = list.execute_time #该批次执行时间点
            # print (type(execute_time))

        elif report_name == "":
            batch_report_obj = Batch_Report.objects.filter(execute_man=execute_man)

            for list in batch_report_obj:
                execute_time_tmp = list.execute_time  # 该批次执行时间点
                execute_time = execute_time_tmp.strftime('%Y-%m-%d')  # 将datatime转成str
                data = {
                    "report_id": list.report_id, "API_total": list.API_total,
                    "pass_total": list.pass_total, "fail_total": list.fail_total,
                    "skip_total": list.skip_total, "execute_man": list.execute_man,
                    "execute_time":execute_time,"report_name":list.report_name
                }
                report_obj_list.append(data)

            content = {"status": "success", "report_list": report_obj_list}

            return JsonResponse(content)
        else:#执行人和报告名都不为空时
            batch_report_obj = Batch_Report.objects.filter(report_name__contains=report_name,execute_man=execute_man)
            for list in batch_report_obj:
                execute_time_tmp = list.execute_time  # 该批次执行时间点
                execute_time = execute_time_tmp.strftime('%Y-%m-%d')  # 将datatime转成str
                data = {
                    "report_id": list.report_id, "API_total": list.API_total,
                    "pass_total": list.pass_total, "fail_total": list.fail_total,
                    "skip_total": list.skip_total, "execute_man": list.execute_man,
                    "execute_time":execute_time,"report_name":list.report_name
                }
                report_obj_list.append(data)

            content = {"status": "success", "report_list": report_obj_list}

            return JsonResponse(content)

    return JsonResponse({"status":"failed"})


def search_execute_log_list(request):
    print ("search_execute_log_list")

    if request.method == "GET":
        report_id = request.GET.get("report_id")
        execute_script_log_objs = Execute_Script_Log.objects.filter(log_report_id_id=report_id) #外键 batch_report report_id

        report_execute_obj_list = []

        for list in execute_script_log_objs:
            data_log = {
                'log_api_name':list.log_api_name,
                'log_execute_script':list.log_execute_script,
                'states':list.status
            }
            report_execute_obj_list.append(data_log)

        batch_report_obj = Batch_Report.objects.filter(report_id=report_id)[0]  # 只能获取一条数据，因为report_id为主键

        execute_time_tmp = batch_report_obj.execute_time  # 该批次执行时间点
        execute_time = execute_time_tmp.strftime('%Y-%m-%d')  # 将datatime转成str
        content = {
            "status": "success","API_total": batch_report_obj.API_total,"report_name":batch_report_obj.report_name,
            "pass_total": batch_report_obj.pass_total, "fail_total": batch_report_obj.fail_total,
            "skip_total": batch_report_obj.skip_total, "execute_man": batch_report_obj.execute_man,
            "execute_time": execute_time,"report_execute_obj_list":report_execute_obj_list
        }

        return JsonResponse(content)


def delete_report_by_reportID(request):
    print ("delete_report_by_reportID")

    if request.method == "GET":
        # TODO 根据权限限制删除
        username = request.GET.get("username")
        print (username)
        authority = UserInfo.objects.filter(username=username)[0].authority #获取该用户的权限等级
        print ("authority:"+authority)
        if "superman" == authority or "primary" == authority:
            report_id = request.GET.get("report_id")
            Execute_Script_Log.objects.filter(log_report_id_id=report_id).delete() #根据report_id删除报告
            Batch_Report.objects.filter(report_id=report_id).delete() #根据report_id删除报告
            content = {"status": "success"}

            return JsonResponse(content)
        elif "secend" == authority:
            content = {"status": "permission"}
            return JsonResponse(content)
        else:
            content = {"status": "error"}
            return JsonResponse(content)


def send_email_by_report_list(request):
    if request.method == "GET":
        report_id = request.GET.get("report_id")
        batch_report_obj = Batch_Report.objects.filter(report_id=report_id)[0]  # 只能获取一条数据，因为report_id为主键
        execute_time_tmp = batch_report_obj.execute_time  # 该批次执行时间点
        execute_time = execute_time_tmp.strftime('%Y-%m-%d')  # 将datatime转成str
        API_total = batch_report_obj.API_total
        report_name = batch_report_obj.report_name
        pass_total = batch_report_obj.pass_total
        fail_total = batch_report_obj.fail_total
        skip_total = batch_report_obj.skip_total
        execute_man = batch_report_obj.execute_man

        print (report_id)

        user_list = request.GET.get("user_list")
        user_list =str(user_list).split(',')
        # print (len(user_list))
        # print (user_list)

        if len(user_list) >0:
            if(user_list[0] == ''):
                content = {"status": "fail"}
                return JsonResponse(content)
            if user_list[-1] == '':
                # 移除空列元素
                user_list.remove('')
            email_list = []
            for list in user_list:
                email_obj_list = Emp_Info.objects.filter(user_id_id=list);

                if len(email_obj_list)>0:
                    email = email_obj_list[0].email
                    email_list.append(email)
                else:
                    content = {"status":"fail"}
                    return JsonResponse(content)
            print (email_list)
            print (type(email_list))
            result = send_mail(report_name=str(report_name),execute_man=str(execute_man),execute_time=str(execute_time),case_total=str(API_total),
                      pass_total=(pass_total),fail_total=str(fail_total),skip_total=str(skip_total),email_list=email_list)

            if(result == "send success"):
                content = {"status": "success"}
            elif result == "send fail":
                content = {"status": "fail"}

            # log_sys.info("[" + str(report_id) + "]测试报告发送邮件 user_list[" + str(user_list) + "]" + str(email_list))
            print ("[" + str(report_id) + "]测试报告发送邮件 user_list[" + str(user_list) + "]" + str(email_list))
        else:
            content = {"status":"fail"}
            return JsonResponse(content)

        # content = {"status": "success"}
        return JsonResponse(content)


def execute_script_result_analysis_fun(rs,script_path,report_id,case_id,API_name
                                       ,passCount,failCount,skipCount):

    try:
        result = rs.split('AutoFW test reslut:')[1].split('\'')[0]
        # result = str(result).replace("\n","")
        print ("---------")
        print (script_path + '：执行结果' + result)
        print ("---------")
        # 修改脚本实例表 脚本状态字段标识
        print(rs)
        if result:
            rs = rs.split('AutoFW test reslut:')[1]
            if "PASS" == result:
                # dict = {"script_status":"PASS"}
                dict = "PASS"
                time_consuming = rs.split('time_consuming:')[1].split(']')[0]
                # log_scripts.info(list + ":PASS:" + " pass message [" + rs.split('PASS')[1] + "]")#响应信息都打印
                log_scripts.info(
                    API_name + ":PASS:[time_consuming:" + time_consuming + "]{ response : \'resultCode" +
                    rs.split('resultCode')[1][1:4] + '\'' + " }")  # 只打印成功关键字段

                execute_script_log = str(
                    API_name) + ":<PASS> [time_consuming:" + time_consuming + "]{ response : \'resultCode" + \
                                     rs.split('resultCode')[1][1:4] + '\'' + " }"

                # 写入Execute_Script_Log表
                dic = {"log_report_id_id": report_id, "log_api_name": API_name,
                       "log_execute_script": execute_script_log, "status": "pass", "bak1": "bak"}
                Execute_Script_Log.objects.create(**dic)
                passCount += 1
            elif "FAILED" == result:
                # dict = {"script_status": "FAILED"}
                dict = "FAILED"
                log_scripts.error(API_name + ":FAILED:" + " error message [" + rs.split('FAILED')[1] + "]")

                execute_script_log = str(API_name) + ":<FAIL> " + " error message 服务器返回错误：[" + \
                                     rs.split('FAILED')[1][1:1500] + "]"  # 设这1-1500为了防止存储字段超过长度
                # 写入Execute_Script_Log表
                dic = {"log_report_id_id": report_id, "log_api_name": API_name,
                       "log_execute_script": execute_script_log, "status": "fail", "bak1": "bak"}
                Execute_Script_Log.objects.create(**dic)
                failCount += 1
        else:
            # dict = {"script_status": "NONE"}
            dict = "NONE"
            execute_script_log = str(API_name) + ":<FAILED> " + " error message [脚本运行出错]"
            # 写入Execute_Script_Log表
            dic = {"log_report_id_id": report_id, "log_api_name": API_name,
                   "log_execute_script": execute_script_log, "status": "skip", "bak1": "bak"}
            Execute_Script_Log.objects.create(**dic)
            skipCount += 1
    except IndexError, e:
        # dict = {"script_status": "NONE"}
        dict = "NONE"
        mylogging("[" + str(API_name) + "] :" + "未获取脚本执行状态，脚本执行失败")
        log_scripts.error(API_name + ":FAILED:" + " error message [ 未获取脚本执行状态，脚本执行失败 ] \r" + rs)

        execute_script_log = str(API_name) + ":<FAILED> " + " error message [脚本运行异常:请查看error.log] \r" + rs
        # 写入Execute_Script_Log表
        dic = {"log_report_id_id": report_id, "log_api_name": str(API_name),
               "log_execute_script": execute_script_log, "status": "skip", "bak1": "bak"}
        Execute_Script_Log.objects.create(**dic)
        skipCount += 1
        # except AttributeError,e:
        #     dict = {"script_status": "NONE"}
        #     mylogging("[" + str(list) + "] :" + "index error,未获取脚本执行状态，脚本执行失败"+e.args)
        #     log_scripts.error(list + ":FAILED:" + " error message [ AttributeError ]"+e.args)
    Script_Info.objects.filter(script_name=API_name).update(script_status=dict)
    Project_Case.objects.filter(case_id=case_id).update(description=dict)  # description 为用例执行状态

    return passCount,failCount,skipCount


def execute_maoyan_script(request):
    if request.method == "GET":
        print ("execute_maoyan_script")
        username = request.GET.get("username")
        send_email_flag = request.GET.get("send_email_flag")
        project_name_maoyan = request.GET.get("project_name_maoyan")
        report_name = request.GET.get("result_name")  # 执行该冒烟测试报告名称
        report_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")#报告ID 唯一值 根据当前时间生成
        maoyan_list = []
        #找出该项目中project_case表中的冒烟测试是否在script_info表中不存在;[未生成相应的测试脚本]
        #select * from project_case a,script_info b where a.project_name_id='project_name_maoyan' and a.case_type='冒烟测试' and a.case_id not in (b.script_case_id_id);
        project_case_obj = Project_Case.objects.extra(
            where=["project_case.project_name_id = %s and project_case.case_type='2' "
                   "and project_case.case_id NOT IN (SELECT script_info.script_case_id_id FROM script_info)"],
            params=[project_name_maoyan]
        )

        #method secand
        # project_case_obj_list = Project_Case.objects.exclude(case_id__in =
        # Script_Info.objects.filter(script_project_name=project_name_maoyan).values_list('script_case_id_id',flat=True))

        if len(project_case_obj)>0:#还有用例未生成测试脚本

            for list in project_case_obj:
                maoyan_list.append(list.case_id)
            log_scripts.error("冒烟测试执行失败 [Caused by :"+project_name_maoyan+" 还有冒烟用例未生成测试脚本，请补充测试脚本！] 请检查以下case_id "+str(maoyan_list))
            # print (maoyan_list)
            #用例表和脚本表匹配是否有没生成脚本的冒烟用例
            content = {"status": "fail","msg":"还有冒烟用例未生成测试脚本，查看脚本日志，请补充测试脚本！"}
            return JsonResponse(content)
        else:
            print ("execute_maoyan_case")
            project_case_maoyan_obj = Project_Case.objects.extra(
                where=["project_case.project_name_id = %s and project_case.case_type='2' "
                       "and project_case.case_id in (select script_info.script_case_id_id from script_info)"],
                params=[project_name_maoyan]
            )
            print (project_case_maoyan_obj)

            passCount = 0
            failCount = 0
            skipCount = 0
            #
            MY_report_name = report_name
            execute_man = username  # 执行人的姓名
            send_email_flag = "yes"  # 否发送邮件标识[只发送给执行用例人]

            # report_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 报告ID 唯一值 根据当前时间生成
            API_total = len(project_case_maoyan_obj)  # 本次冒烟测试执行的总API数
            execute_time = datetime.datetime.now()  # 执行当前时间

            dict_report_id = {"report_id": report_id, "report_name": MY_report_name, "API_total": str(API_total),
                              "pass_total": str(passCount), "fail_total": str(failCount),
                              "skip_total": str(skipCount),
                              "execute_man": str(execute_man),
                              "execute_time": execute_time, "bak1": "bak", "bak2": "bak"}

            Batch_Report.objects.create(**dict_report_id)

            for list in project_case_maoyan_obj:
                # maoyan_list.append(list.case_id)
                script_info_obj = Script_Info.objects.filter(script_case_id=list.case_id)[0]
                script_path = script_info_obj.script_path
                API_name = script_info_obj.script_case_name
                case_id = script_info_obj.script_case_id

                rs = execute_script_Popen(script_path,0.1)

                passCount,failCount,skipCount = execute_script_result_analysis_fun(rs,script_path,report_id,case_id,API_name,passCount,failCount,skipCount)


            content = {"status": "execute_script_success"}

            # 报告名 执行者 api总数 执行时间 执行报告ID
            print("result_name=%s execute_name=%s api_total=%s"
                  " execute_time=%s report_id=%s" % (report_name, execute_man, str(API_total), execute_time, report_id))
            # pass fail skip
            # print("passCount=%s failCount=%s skipCount=%s"%(passCount,failCount,skipCount))

            dict_execute = {"report_id": report_id, "report_name": report_name, "API_total": str(API_total),
                            "pass_total": str(passCount), "fail_total": str(failCount), "skip_total": str(skipCount),
                            "execute_man": str(execute_man),
                            "execute_time": execute_time, "bak1": "bak", "bak2": "bak"}

            Batch_Report.objects.filter(report_id=report_id).update(**dict_execute)

            # -------start-------发送测试报告邮件---------------------
            execute_time = execute_time.strftime("%Y%m%d%H%M%S")
            emp_obj_list = Emp_Info.objects.filter(user_id_id=execute_man)  # 主键，只有一条数据
            if send_email_flag == "yes":
                if emp_obj_list.exists():
                    email_adr_list = []
                    for list in emp_obj_list:
                        emails = list.email
                        email_adr_list.append(emails)
                    send_mail(report_name, execute_man, execute_time, str(API_total), str(passCount),
                              str(failCount),
                              str(skipCount), email_adr_list)
                else:
                    print ("该用户没有邮箱信息！")
                    content = {"status": "email_send_fail","msg":"该用户为填写邮箱信息，请去用户中心补填邮箱信息！"}
            # -------end-------发送测试报告邮件---------------------
            return JsonResponse(content)


def execute_huigui_script(request):
    if request.method == 'GET':
        print ("execute_maoyan_script")
        username = request.GET.get("username")
        send_email_flag = request.GET.get("send_email_flag")
        project_name_huigui = request.GET.get("project_name_huigui")
        report_name = request.GET.get("result_name")  # 执行该冒烟测试报告名称
        report_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 报告ID 唯一值 根据当前时间生成

        huigui_list = []
        # 找出该项目中project_case表中的回归测试是否在script_info表中不存在;[未生成相应的测试脚本]
        # select * from project_case a,script_info b where a.project_name_id='project_name_huigui' and a.case_type='回归测试' and a.case_id not in (b.script_case_id_id);
        project_case_obj = Project_Case.objects.extra(
            where=["project_case.project_name_id = %s and project_case.case_type='1' "
                   "and project_case.case_id NOT IN (SELECT script_info.script_case_id_id FROM script_info)"],
            params=[project_name_huigui]
        )

        if len(project_case_obj)>0:#还有回归测试用例未生成测试脚本
            for list in project_case_obj:
                huigui_list.append(list.case_id)
            log_scripts.error("回归测试执行失败 [Caused by :"+project_name_huigui+" 还有冒烟用例未生成测试脚本，请补充测试脚本！] 请检查以下case_id "+str(huigui_list))
            # print (maoyan_list)
            #用例表和脚本表匹配是否有没生成脚本的冒烟用例
            content = {"status": "fail","msg":"还有冒烟用例未生成测试脚本，查看脚本日志，请补充测试脚本！"}
            return JsonResponse(content)
        else:
            print ("execute_huigui_case")
            project_case_huigui_obj = Project_Case.objects.extra(
                where=["project_case.project_name_id = %s and project_case.case_type='1' "
                       "and project_case.case_id in (select script_info.script_case_id_id from script_info)"],
                params=[project_name_huigui]
            )
            print (project_case_huigui_obj)

            passCount = 0
            failCount = 0
            skipCount = 0
            #
            HG_report_name = report_name
            execute_man = username  # 执行人的姓名
            send_email_flag = "yes"  # 否发送邮件标识[只发送给执行用例人]

            # report_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 报告ID 唯一值 根据当前时间生成
            API_total = len(project_case_huigui_obj)  # 本次冒烟测试执行的总API数
            execute_time = datetime.datetime.now()  # 执行当前时间

            dict_report_id = {"report_id": report_id, "report_name": HG_report_name, "API_total": str(API_total),
                              "pass_total": str(passCount), "fail_total": str(failCount),
                              "skip_total": str(skipCount),
                              "execute_man": str(execute_man),
                              "execute_time": execute_time, "bak1": "bak", "bak2": "bak"}

            Batch_Report.objects.create(**dict_report_id)

            for list in project_case_huigui_obj:
                # maoyan_list.append(list.case_id)
                script_info_obj = Script_Info.objects.filter(script_case_id=list.case_id)[0]
                script_path = script_info_obj.script_path
                API_name = script_info_obj.script_case_name
                case_id = script_info_obj.script_case_id

                rs = execute_script_Popen(script_path,0.1)

                passCount,failCount,skipCount = execute_script_result_analysis_fun(rs,script_path,report_id,case_id,API_name,passCount,failCount,skipCount)


            content = {"status": "execute_script_success"}

            # 报告名 执行者 api总数 执行时间 执行报告ID
            print("result_name=%s execute_name=%s api_total=%s"
                  " execute_time=%s report_id=%s" % (report_name, execute_man, str(API_total), execute_time, report_id))
            # pass fail skip
            # print("passCount=%s failCount=%s skipCount=%s"%(passCount,failCount,skipCount))

            dict_execute = {"report_id": report_id, "report_name": report_name, "API_total": str(API_total),
                            "pass_total": str(passCount), "fail_total": str(failCount), "skip_total": str(skipCount),
                            "execute_man": str(execute_man),
                            "execute_time": execute_time, "bak1": "bak", "bak2": "bak"}

            Batch_Report.objects.filter(report_id=report_id).update(**dict_execute)

            # -------start-------发送测试报告邮件---------------------
            execute_time = execute_time.strftime("%Y%m%d%H%M%S")
            emp_obj_list = Emp_Info.objects.filter(user_id_id=execute_man)  # 主键，只有一条数据
            if send_email_flag == "yes":
                if emp_obj_list.exists():
                    email_adr_list = []
                    for list in emp_obj_list:
                        emails = list.email
                        email_adr_list.append(emails)
                    send_mail(report_name, execute_man, execute_time, str(API_total), str(passCount),
                              str(failCount),
                              str(skipCount), email_adr_list)
                else:
                    print ("该用户没有邮箱信息！")
                    content = {"status": "email_send_fail","msg":"该用户为填写邮箱信息，请去用户中心补填邮箱信息！"}
            # -------end-------发送测试报告邮件---------------------
            return JsonResponse(content)