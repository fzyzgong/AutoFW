#coding=utf-8
import json
import datetime,time
import os
import xlrd
#import paramiko

from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from .util.execute_script_Popen import execute_script_Popen
from .util.copyFileAndUpdataUtil import copyFile
from .util.send_mail_batch_report import send_mail
from .util.execute_interface import Execute_Interface
from .util.execute_fixed_interface import Execute_Fixed_Interface
from .util.login_get_userinfo import LoginGetUserInfo
from .util.parse_har_file import Parse_har_file_to_request
from models import *
from django.db.models import Q
import MySQLdb
import traceback
import sys


reload(sys)
sys.setdefaultencoding('utf8')
from .util.Mylogging import Mylogging  #自定义异常捕获日志

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
    case_name = request.POST.get("case_name")#获取点击search传点过来的case_name
    #判断是否按接口名查询结果
    if case_name is None:
        project_case_all = Project_Case.objects.filter(project_name=obj_project_name)
    else:
        project_case_all = Project_Case.objects.filter(project_name=obj_project_name,case_name__contains=case_name)
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
    json_data_case_list = {'rows':caseList,'total':caseList_len}#easyui 接收参数格式 rows/total
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

        try:
            Project_Case.objects.create(**dic)
            log_sys.info(str(username) + "添加API用例 [" + str(case_name) + "] 属于项目：[" + project_id + "]")
            return HttpResponse("save")
        except:
            print traceback.format_exc()
            return HttpResponse("error")
    else:
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
    content = {"project_name_list":project_qs,"creator_list":creator,"username":username}

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
    # unicode转str
    project_module = project_module.encode("utf8")
    case_status = get("case_status")
    case_name = get("case_name")
    # print (project_name)
    # print (creator_name)
    # print (project_module)
    # print (str(case_status))
    # print (str(case_name))
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

    # 所属模块/创建者/接口状态/接口名 为空时查询分支
    if project_module == "" and creator_name == "" and str(case_status) == "" and str(case_name) == "":
        print ("创建者/接口状态/接口名 为空时查询分支")
        case_obj = Project_Case.objects.filter(project_name=project_name)
        for list in case_obj:
            case_obj_dict = {"case_id":list.case_id,"case_name":list.case_name,"project_name":list.project_name_id,"module_name":list.module_name_id,
                             "url_path":list.url_path,"method":list.method,"headers":list.headers,"ip":prject_config_ip,"parameter_format":list.parameter_format,"parameter":list.parameter,
                             "expected":list.expected,"port":prject_config_port,"creator":list.creator,"case_status":list.description}
            case_obj_list.append(case_obj_dict)
        # print (case_obj_list)
        content = {"status": "success", "case_list": case_obj_list}
        print (content)
        return JsonResponse(content)
    # 所属模块/创建者/接口状态 为空时查询分支
    if project_module == "" and creator_name == "" and str(case_status) == "":
        print ("所属模块/创建者/接口状态 为空时查询分支")
        case_obj = Project_Case.objects.filter(project_name=project_name,case_name__contains=case_name)
        for list in case_obj:
            case_obj_dict = {"case_id":list.case_id,"case_name":list.case_name,"project_name":list.project_name_id,"module_name":list.module_name_id,
                             "url_path":list.url_path,"method":list.method,"headers":list.headers,"ip":prject_config_ip,"parameter_format":list.parameter_format,"parameter":list.parameter,
                             "expected":list.expected,"port":prject_config_port,"creator":list.creator,"case_status":list.description}
            case_obj_list.append(case_obj_dict)
        # print (case_obj_list)
        content = {"status": "success", "case_list": case_obj_list}
        print (content)
        return JsonResponse(content)
    # 所属模块/接口状态 为空时查询分支
    if project_module == "" and str(case_status) == "":
        print ("所属模块/接口状态 为空时查询分支")
        # 获取用户id
        creator_n = Emp_Info.objects.filter(name=creator_name)[0].user_id_id
        print (creator_n)
        case_obj = Project_Case.objects.filter(project_name=project_name, case_name__contains=case_name,creator=creator_n)
        for list in case_obj:
            case_obj_dict = {"case_id": list.case_id, "case_name": list.case_name,
                             "project_name": list.project_name_id, "module_name": list.module_name_id,
                             "url_path": list.url_path, "method": list.method, "headers": list.headers,
                             "ip": prject_config_ip, "parameter_format": list.parameter_format,
                             "parameter": list.parameter,
                             "expected": list.expected, "port": prject_config_port, "creator": list.creator,
                             "case_status": list.description}
            case_obj_list.append(case_obj_dict)
        # print (case_obj_list)
        content = {"status": "success", "case_list": case_obj_list}
        print (content)
        return JsonResponse(content)

    # 所属模块 为空时查询分支
    if project_module == "":
        print ("所属模块/接口状态 为空时查询分支")
        # 获取用户id
        creator_n = Emp_Info.objects.filter(name=creator_name)[0].user_id_id
        print (creator_n)
        case_obj = Project_Case.objects.filter(project_name=project_name, case_name__contains=case_name,
                                               creator=creator_n,description=case_status)
        for list in case_obj:
            case_obj_dict = {"case_id": list.case_id, "case_name": list.case_name,
                             "project_name": list.project_name_id, "module_name": list.module_name_id,
                             "url_path": list.url_path, "method": list.method, "headers": list.headers,
                             "ip": prject_config_ip, "parameter_format": list.parameter_format,
                             "parameter": list.parameter,
                             "expected": list.expected, "port": prject_config_port, "creator": list.creator,
                             "case_status": list.description}
            case_obj_list.append(case_obj_dict)
        # print (case_obj_list)
        content = {"status": "success", "case_list": case_obj_list}
        print (content)
        return JsonResponse(content)

    #创建者/用例状态/用例名 为空时查询分支
    if creator_name == "" and str(case_status) == "" and str(case_name) == "":
        print ("创建者/接口状态/接口名 为空时查询分支")
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
    # 创建者/接口状态 为空时查询分支
    elif creator_name == "" and str(case_status) == "":
        print ("创建者/接口状态 为空时查询分支")
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
    # 创建者/接口名称 为空时查询分支
    elif creator_name == "" and str(case_name) == "":
        print ("创建者/接口名称 为空时查询分支")
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
    # 接口名称/接口状态 为空时查询分支
    elif str(case_status) == "" and str(case_name) == "":
        print ("接口名称/接口状态 为空时查询分支")
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
    # 接口状态 为空时查询分支
    elif case_status == "":
        print ("接口状态 为空时查询分支")
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
    # 接口名称 为空时查询分支
    elif case_name == "":
        print ("接口名称 为空时查询分支")
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


#执行调用接口（接口带有固定参数）
def chose_all_execute_test_interface(request):
    print ("chose_all_execute_test_interface")
    if request.method == "GET":
        case_id = request.GET.get("case_id_json")
        case_id_list = str(case_id).split(',')
        # 移除空列元素
        case_id_list.remove('')

        system_info_initialization = request.GET.get("system_info_initialization")

        # 执行用例前先获取用户token  系统信息初始化
        if system_info_initialization != '':
            try:
                system_info_initialization = json.loads(system_info_initialization)  # 字符串转字典

            except:
                print(traceback.format_exc())
                Mylogging.interface("----系统信息初始化  字符串转字典异常----------\r\n")
                Mylogging.interface(traceback.format_exc())

                return JsonResponse({"status": "failed", "msg": "接口执行失败，传入参数有误[非json格式]"})

            userinfo_dict = LoginGetUserInfo.login_get_userinfo(**system_info_initialization)

            if userinfo_dict == "init_failed":
                print("用例执行前初始化信息失败[获取验证码失败]")

                return JsonResponse({"status": "failed", "msg": "接口执行失败,初始化信息失败[获取验证码失败]"})

            # YHB_userInfo = userinfo_dict['YHB_userInfo']
            # JJB_userInfo = userinfo_dict['JJB_userInfo']
            print ("#################### 接口执行前获取用户信息：%s" % (userinfo_dict))
            Mylogging.interface("--------------------------------------------------------------------------\r\n")
            Mylogging.interface("#################### 接口执行前获取用户信息：%s" % (userinfo_dict))
            Mylogging.interface("--------------------------------------------------------------------------\r\n")
        else:
            userinfo_dict = {}
            print ("#################### 接口执行前 不需要初始化系统信息#######################")
            Mylogging.interface("--------------------------------------------------------------------------\r\n")
            Mylogging.interface("#################### 接口执行前 不需要初始化系统信息#######################")


        passCount = 0
        failCount = 0
        skipCount = 0

        report_name = request.GET.get("result_name")  # 执行该批次的测试报告名称
        execute_man = request.GET.get("username")  # 获取执行人的姓名
        print execute_man
        report_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 报告ID 唯一值 根据当前时间生成
        API_total = len(case_id_list)  # 本次执行的总API数
        execute_time = datetime.datetime.now()  # 执行当前时间

        dict_report_id = {"report_id": report_id, "report_name": report_name, "API_total": str(API_total),
                          "pass_total": str(passCount), "fail_total": str(failCount), "skip_total": str(skipCount),
                          "execute_man": str(execute_man),
                          "execute_time": execute_time, "bak1": "bak", "bak2": "bak"}

        Batch_Report.objects.create(**dict_report_id)



        try:
            for interface in case_id_list:
                IMPL_obj = Project_Case.objects.filter(case_id=interface)[0]
                project_name = IMPL_obj.project_name_id
                project_obj = Project.objects.filter(project_name=project_name)[0]
                project_id = project_obj.project_code
                project_config_obj = Project_Config.objects.filter(project_id=project_id)[0]

                ip = str(project_config_obj.ip)
                domain = project_config_obj.domain.replace(' ', '')  # 去除空格
                protocol = project_config_obj.protocol.replace(' ', '')  # 去除空格
                url_path = str(IMPL_obj.url_path).replace(' ', '')  # 去除空格
                method = str(IMPL_obj.method).replace(' ', '')  # 去除空格

                # headers 和 param 可以为空 GET/POST 不同时分支
                headers = str(IMPL_obj.headers)
                parameter_format = str(IMPL_obj.parameter_format)
                parameter = str(IMPL_obj.parameter)
                expected = str(IMPL_obj.expected)

                print (headers, parameter, expected)
                url = str(protocol) + '://' + str(domain) + url_path

                try:
                    api_log = Execute_Fixed_Interface.execute_interface(url=url, method=method, parameter_format=parameter_format, headers=headers, parameter=parameter, expected=expected, project_name=project_name, user_info=userinfo_dict)
                    Mylogging.interface("[接口日志] ["+interface+"]"+api_log)
                    Mylogging.interface("--------------------------------------------------------------------------\r\n")
                    exe_status = str(api_log).split('\'')[0].split(':')[1]
                    print exe_status
                    if 'PASS' == str(exe_status):
                        passCount += 1
                    elif 'FAILED' == str(exe_status):
                        failCount += 1
                    elif 'SKIP' == str(exe_status):
                        skipCount += 1
                    execute_script_log_dict = {"log_report_id_id":report_id,"log_api_name":interface,"log_execute_script":api_log,
                                               "bak1":"1","status":str(exe_status)}
                    Execute_Script_Log.objects.create(**execute_script_log_dict)
                    Project_Case.objects.filter(case_id=interface).update(description=exe_status)
                except:
                    print traceback.print_exc()
                    Project_Case.objects.filter(case_id=interface).update(description="SKIP")

            dict_execute = {"report_id": report_id, "report_name": report_name, "API_total": str(API_total),
                            "pass_total": str(passCount), "fail_total": str(failCount), "skip_total": str(skipCount),
                            "execute_man": str(execute_man),
                            "execute_time": execute_time, "bak1": "bak", "bak2": "bak"}

            Batch_Report.objects.filter(report_id=report_id).update(**dict_execute)
            content = {
                "status":"success",
                "msg":"调用接口成功"
            }
            return JsonResponse(content)
        except:
            content = {
                "status": "failed",
                "msg":str(traceback.format_exc())
            }
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
            print (script_path)
            # project_case_name = script_info_obj.script_case_name
            script_case_id = script_info_obj.script_case_id_id
            print (script_case_id)
            rs = execute_script_Popen(script_path, 0.1)
            #------------动态传参------------start-------------------------------
            # project_case_obj = Project_Case.objects.filter(case_id=script_case_id)[0]
            # if "TBSAccessToken" in project_case_obj.headers:
            #     # print (script_path)
            #     rs = execute_script_Popen(script_path,0.1,TBS_token=True) #脚本路径/休眠时间/ 是否需要动态传参数
            # else:
            #     rs = execute_script_Popen(script_path, 0.1, TBS_token=False)
            # print(rs)
            # ------------动态传参------------end-------------------------------


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
        #         Mylogging.error("["+str(list)+"] :"+"未获取脚本执行状态，脚本执行失败")
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
        #     #     Mylogging.error("[" + str(list) + "] :" + "index error,未获取脚本执行状态，脚本执行失败"+e.args)
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

#生成用例页面跳转
def yongli_genirate_page(request,username):
    print ("yongli_genirate_page")
    #项目名称ValuesQuerySet
    project_qs = Project.objects.values("project_name")
    #获取成员姓名
    creator = Emp_Info.objects.values("name")

    # print (creator)
    content = {"project_name_list":project_qs,"username":username}

    return render(request,"AutoFW/yongli_genirate_page.html",content)


#执行用例页面跳转
def execute_yongli_page(request,username):
    print ("yongli_genirate_page")
    # 项目名称ValuesQuerySet
    project_qs = Project.objects.values("project_name")
    content = {"project_name_list":project_qs,"username":username}
    return render(request,"AutoFW/yongli_execution_page.html",content)


#修改用例页面跳转
def yongli_update_page(request,username):
    print("yongli_genirate_page")
    # 项目名称ValuesQuerySet
    project_qs = Project.objects.values("project_name")
    content = {"project_name_list":project_qs,"username":username}
    return render(request,"AutoFW/yongli_update_page.html",content)


#har方式调用接口
def har_file_page(request,username):
    print("har_file_page")
    content = {"username": username}
    return render(request, "AutoFW/har_file_page.html",content)


#查询har文件路径并展示
def search_har_file(request):
    print("search_har_file")
    if request.method == "GET":
        file_path = request.GET.get("file_path")
        search_type = request.GET.get("search_type")#0只获取当前目录文件  1递归查询子目录文件
        print(file_path)
        print(search_type)

        har_list = []

        if search_type == '0':
            file_list = os.listdir(file_path) #只获取当强目录下文件名
            for f in file_list[:]:
                if os.path.splitext(f)[1] != '.har':
                    file_list.remove(f)

            for f in file_list:
                file_detail_dict = {}
                file_detail_dict['file_n'] = f
                file_detail_dict['file_p'] = os.path.join(file_path,f)
                har_list.append(file_detail_dict)
        else:
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    file_detail_dict = {}
                    if os.path.splitext(file)[1] == '.har':
                        file_detail_dict['file_n'] = file
                        file_detail_dict['file_p'] = os.path.join(root, file)
                        har_list.append(file_detail_dict)

        print(har_list)

        content = {"status":"success","har_list":har_list}
        return JsonResponse(content)


#调用执行har文件
def execution_har_file(request):
    print("execution_har_file")
    if request.method == "GET":
        username = request.GET.get("username")
        har_path_json = request.GET.get("har_path_json")
        result_name = request.GET.get("result_name")
        system_info_initialization = request.GET.get("system_info_initialization")

        #print(username,har_path_json,result_name,system_info_initialization)

        har_path_json_list = str(har_path_json).split(',')
        har_path_json_list.remove('')  # 移除最后一个空元素

        user_info_dict = Parse_har_file_to_request.get_userinfo(system_info_initialization)

        token = user_info_dict['accessToken']

        for har_f in har_path_json_list:
            response_text = Parse_har_file_to_request.parse_har(har_f,token)
            print(response_text)


        content = {"status":"success","msg":"调用成功"}
        return JsonResponse(content)





#根据project_case_id查询用例
def search_case_by_case_id(request):
    print ("search_case_by_case_id")
    if request.method == "GET":
        script_case_id = request.GET.get("script_case_id")

        if script_case_id != "":
            script_case_obj = Script_Case_Info.objects.filter(script_case_id=script_case_id) #唯一值


            if len(script_case_obj) > 0:
                case = script_case_obj[0]
                print type(case.status)

                project_case_dict = {"script_case_id":case.script_case_id,"script_case_name":case.script_case_name,
                                     "execution_order":case.execution_order,"config":case.config,"parameter_ddt":case.parameter_ddt,
                                     "status":str(case.status),"script_case_type":case.script_case_type,"script_case_project_name_id":
                                     case.script_case_project_name_id,"script_case_module_name_id":case.script_case_module_name_id,
                                    "creator":case.creator,"remark":case.remark}

                content = {"status":"success","msg":"search successful","project_case_dict":project_case_dict}

                return JsonResponse(content)
            else:
                content = {"status": "failed", "msg": "查询结果：用例编号不存在"}
                return JsonResponse(content)
        else:
            content = {"status": "error", "msg": "用例编号为空"}
            return JsonResponse(content)


#修改用例
def update_script_case(request):
    print ("update_script_case")
    if request.method == "GET":
        script_case_id = request.GET.get("script_case_id")
        script_case_name = request.GET.get("script_case_name")
        execution_order = request.GET.get("execution_order")
        config = request.GET.get("config")
        parameter_ddt = request.GET.get("parameter_ddt")
        status = request.GET.get("status")
        script_case_type = request.GET.get("script_case_type")
        script_case_project_name_id = request.GET.get("script_case_project_name_id")
        script_case_module_name_id = request.GET.get("script_case_module_name_id")
        creator = request.GET.get("creator")
        remark = request.GET.get("remark")
        content = {"status": "status", "msg": "msg"}
        if script_case_name != '' and execution_order != '' and status != '' and script_case_type != '':


            project_case_dict = {"script_case_id": script_case_id, "script_case_name": script_case_name,
                                 "execution_order": execution_order, "config": config,
                                 "parameter_ddt": parameter_ddt,
                                 "status": str(status), "script_case_type": script_case_type,
                                 "script_case_project_name_id":
                                     script_case_project_name_id,
                                 "script_case_module_name_id": script_case_module_name_id,
                                 "creator": creator, "remark": remark}

            try:
                Script_Case_Info.objects.filter(script_case_id=script_case_id).update(**project_case_dict)
                content['status'] = "success"
                content['msg'] = "更新用例成功"
            except:
                content['status'] = "error"
                content['msg'] = "更新用例失败:"+str(traceback.format_exc())
                return JsonResponse(content)
        else:
            content['status'] = "failed"
            content['msg'] = "更新用例失败,字段为空"
            return JsonResponse(content)

        return JsonResponse(content)





#查询接口
def search_interface(request):
    print ("search_interface")
    if request.method == "GET":
        interface_name = request.GET.get("interface_name")
        project_name = request.GET.get("project_name")
        if project_name != "":
            project_case_obj = Project_Case.objects.filter(case_id__contains=interface_name,project_name=project_name)
            if len(project_case_obj)>0:
                interface_list = []
                for list in project_case_obj:
                    interface_dic = {
                        "case_id":list.case_id,
                        "headers":list.headers,
                        "parameter":list.parameter,
                        "method":list.method,
                        "url_path":list.url_path
                    }
                    interface_list.append(interface_dic)
                print (interface_list)
                return JsonResponse({"status":"success","interface_list":interface_list})
            else:
                return JsonResponse({"status": "failed", "msg": "未查询到相关接口"})
        else:
            return JsonResponse({"status":"error","msg":"项目名称不能为空"})


def add_script_case(request):
    print ("add_script_case")
    creator = request.GET.get("creator")
    if request.method == "GET":
        case_id = request.GET.get("case_id")
        case_name = request.GET.get("case_name")
        project_name = request.GET.get("project_name")
        project_module = request.GET.get("project_module")
        execution_order = request.GET.get("execution_order")
        parameter_ddt = request.GET.get("parameter_ddt")
        catch_var = request.GET.get("catch_var")
        case_type = request.GET.get("case_type")
        remark = request.GET.get("remark")

        print ("case_id=%s,case_name=%s,project_name=%s,project_module=%s,execution_order=%s,parameter_ddt=%s,catch_var=%s,creator=%s,case_type=%s,remark=%s"
               %(case_id,case_name,project_name,project_module,execution_order,parameter_ddt,catch_var,creator,case_type,remark))

        dict = {
            "script_case_id":case_id,
            "script_case_name":case_name,
            "script_case_project_name_id":project_name.replace(' ', ''),
            "script_case_module_name_id":project_module.replace(' ', ''),
            "execution_order":execution_order,
            "parameter_ddt":parameter_ddt,
            "config":catch_var,
            "creator":creator,
            "status":"None",
            "script_case_type":case_type,
            "remark":remark
        }

        sci_obj = Script_Case_Info.objects.filter(Q(script_case_id=case_id) | Q(script_case_name=case_name))

        if len(sci_obj)>0:
            return JsonResponse({"status": "unique_error", "msg": "用例编号或用例名称主键冲突"})

        if '' == case_id or '' == case_name or '' == project_name or '' == project_module or '' == execution_order or '' == creator or '' == case_type:
            return JsonResponse({"status": "null_error", "msg": "提交数据存在空值"})

        Script_Case_Info.objects.create(**dict)
        return JsonResponse({"status": "success", "msg": "新增用例成功"})
    else:
        return JsonResponse({"status": "failed", "msg": "新增用例失败"})


def search_exe_case(request):
    print ("search_exe_case")
    if request.method == "GET":
        project_name = request.GET.get("project_name")
        project_module = request.GET.get("project_module")
        project_case_name = request.GET.get("project_case_name")
        project_case_type = request.GET.get("project_case_type")

        print ("project_name=%s,project_module=%s,project_case_name=%s,project_case_type=%s"%(project_name,project_module,project_case_name,project_case_type))

        if '' == project_name:
            return JsonResponse({"status": "project_name_null", "msg": "项目不能为空"})

        elif '' == project_module and '' == project_case_name and '' == project_case_type:
            sci_obj = Script_Case_Info.objects.filter(script_case_project_name_id=project_name)
            print (len(sci_obj))
            if len(sci_obj) > 0:
                sci_list = []
                for list in sci_obj:
                    case_dict = {
                        "script_case_id":list.script_case_id,
                        "script_case_name":list.script_case_name,
                        "script_case_project_name_id":list.script_case_project_name.project_name,#外键
                        "script_case_module_name_id": list.script_case_module_name.module_name,#外键
                        "execution_order":list.execution_order,
                        "parameter_ttd": list.parameter_ddt,
                        "config":list.config,
                        "creator":list.creator,
                        "status":list.status,
                        "script_case_type":list.script_case_type,
                        "remark":list.remark
                    }
                    sci_list.append(case_dict)
            else:
                return JsonResponse({"status":"no_date","msg":"该项目没有用例"})

        elif '' == project_module and '' == project_case_type and '' != project_case_name:
            sci_obj = Script_Case_Info.objects.filter(script_case_project_name_id=project_name,script_case_id__contains=project_case_name)
            if len(sci_obj) > 0:
                sci_list = []
                for list in sci_obj:
                    case_dict = {
                        "script_case_id": list.script_case_id,
                        "script_case_name": list.script_case_name,
                        "script_case_project_name_id": list.script_case_project_name.project_name,#外键
                        "script_case_module_name_id": list.script_case_module_name.module_name,#外键
                        "execution_order": list.execution_order,
                        "parameter_ttd": list.parameter_ddt,
                        "config": list.config,
                        "creator": list.creator,
                        "status": list.status,
                        "script_case_type": list.script_case_type,
                        "remark": list.remark
                    }
                    sci_list.append(case_dict)
            else:
                return JsonResponse({"status": "no_date", "msg": "没有匹配到用例"})
        elif '' == project_case_name and '' == project_case_type and '' != project_module:
            sci_obj = Script_Case_Info.objects.filter(script_case_project_name_id=project_name,script_case_module_name_id=project_module)
            if len(sci_obj) > 0:
                sci_list = []
                for list in sci_obj:
                    case_dict = {
                        "script_case_id": list.script_case_id,
                        "script_case_name": list.script_case_name,
                        "script_case_project_name_id": list.script_case_project_name.project_name,#外键
                        "script_case_module_name_id": list.script_case_module_name.module_name,#外键
                        "execution_order": list.execution_order,
                        "parameter_ttd": list.parameter_ddt,
                        "config": list.config,
                        "creator": list.creator,
                        "status": list.status,
                        "script_case_type": list.script_case_type,
                        "remark": list.remark
                    }
                    sci_list.append(case_dict)
            else:
                return JsonResponse({"status": "no_date", "msg": "该模块没有用例"})
        elif '' == project_case_name and '' != project_case_type and '' != project_module:

            sci_obj = Script_Case_Info.objects.filter(script_case_project_name_id=project_name,script_case_module_name_id=project_module,script_case_type=project_case_type)
            if len(sci_obj) > 0:
                sci_list = []
                for list in sci_obj:
                    case_dict = {
                        "script_case_id": list.script_case_id,
                        "script_case_name": list.script_case_name,
                        "script_case_project_name_id": list.script_case_project_name.project_name,#外键
                        "script_case_module_name_id": list.script_case_module_name.module_name,#外键
                        "execution_order": list.execution_order,
                        "parameter_ttd": list.parameter_ddt,
                        "config": list.config,
                        "creator": list.creator,
                        "status": list.status,
                        "script_case_type": list.script_case_type,
                        "remark": list.remark
                    }
                    sci_list.append(case_dict)
            else:
                return JsonResponse({"status": "no_date", "msg": "该模块没有用例"})
        elif '' == project_case_name and '' != project_case_type and '' == project_module:

            sci_obj = Script_Case_Info.objects.filter(script_case_project_name_id=project_name,
                                                      script_case_type=project_case_type)
            if len(sci_obj) > 0:
                sci_list = []
                for list in sci_obj:
                    case_dict = {
                        "script_case_id": list.script_case_id,
                        "script_case_name": list.script_case_name,
                        "script_case_project_name_id": list.script_case_project_name.project_name,  # 外键
                        "script_case_module_name_id": list.script_case_module_name.module_name,  # 外键
                        "execution_order": list.execution_order,
                        "parameter_ttd": list.parameter_ddt,
                        "config": list.config,
                        "creator": list.creator,
                        "status": list.status,
                        "script_case_type": list.script_case_type,
                        "remark": list.remark
                    }
                    sci_list.append(case_dict)
            else:
                return JsonResponse({"status": "no_date", "msg": "该模块没有用例"})
        elif '' != project_case_name and '' != project_case_type and '' != project_module:

            sci_obj = Script_Case_Info.objects.filter(script_case_project_name_id=project_name,
                                                      script_case_module_name_id=project_module,
                                                      script_case_type=project_case_type,script_case_id__contains=project_case_name)
            if len(sci_obj) > 0:
                sci_list = []
                for list in sci_obj:
                    case_dict = {
                        "script_case_id": list.script_case_id,
                        "script_case_name": list.script_case_name,
                        "script_case_project_name_id": list.script_case_project_name.project_name,  # 外键
                        "script_case_module_name_id": list.script_case_module_name.module_name,  # 外键
                        "execution_order": list.execution_order,
                        "parameter_ttd": list.parameter_ddt,
                        "config": list.config,
                        "creator": list.creator,
                        "status": list.status,
                        "script_case_type": list.script_case_type,
                        "remark": list.remark
                    }
                    sci_list.append(case_dict)
            else:
                return JsonResponse({"status": "no_date", "msg": "该模块没有用例"})

        return JsonResponse({"status": "success", "case_list":sci_list})


def execution_test_case(request):
    print ("execution_test_case")
    if request.method == "GET":
        passCount = 0
        failCount = 0
        skipCount = 0

        script_case_name_json = request.GET.get("script_case_name_json")
        report_name = request.GET.get("result_name")
        send_email_flag = request.GET.get("send_email_flag")#是否发送邮件
        username = request.GET.get("username")#执行人
        system_info_initialization = request.GET.get("system_info_initialization")#用例执行前 系统初始化值

        # if system_info_initialization != '':
        #     system_info_initialization = eval(system_info_initialization)
        #     print(system_info_initialization)
        #     print(type(system_info_initialization))
        #
        # return 0

        script_case_name_list = str(script_case_name_json).split(',')
        script_case_name_list.remove('')#移除最后一个空元素

        report_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 报告ID 唯一值 根据当前时间生成
        case_total = len(script_case_name_list)  # 本次执行的总API数
        execute_time = datetime.datetime.now()  # 执行当前时间

        dict_report = {"report_id": report_id, "report_name": report_name, "case_total": str(case_total),
                          "pass_total": str(passCount), "fail_total": str(failCount), "skip_total": str(skipCount),
                          "execute_man": str(username),
                          "execute_time": execute_time, "bak1": "bak", "bak2": "bak"}

        Case_Execution_Report.objects.create(**dict_report)
        print ("所有需要执行的用例"+str(script_case_name_list))
        print (dict_report)
        # try:
        #执行用例前先获取用户token  系统信息初始化
        if system_info_initialization != '':
            try:
                system_info_initialization = json.loads(system_info_initialization)#字符串转字典
            except:
                print(traceback.format_exc())
                Mylogging.interface("----系统信息初始化  字符串转字典异常----------\r\n")
                Mylogging.interface(traceback.format_exc())

                return JsonResponse({"status":"failed","msg":"用例执行失败，传入参数有误[非json格式]"})

            userinfo_dict = LoginGetUserInfo.login_get_userinfo(**system_info_initialization)

            if userinfo_dict == "init_failed":
                print("用例执行前初始化信息失败[获取验证码失败]")

                return JsonResponse({"status": "failed", "msg": "用例执行失败,初始化信息失败[获取验证码失败]"})

            # YHB_userInfo = userinfo_dict['YHB_userInfo']
            # JJB_userInfo = userinfo_dict['JJB_userInfo']
            print ("#################### 用例执行前获取用户信息：%s"%(userinfo_dict))
            Mylogging.interface("--------------------------------------------------------------------------\r\n")
            Mylogging.interface("#################### 用例执行前获取用户信息：%s"%(userinfo_dict))
            Mylogging.interface("--------------------------------------------------------------------------\r\n")
        else:
            userinfo_dict = {}
            print ("#################### 用例执行前 不需要初始化系统信息#######################")
            Mylogging.interface("--------------------------------------------------------------------------\r\n")
            Mylogging.interface("#################### 用例执行前 不需要初始化系统信息#######################")

        #获取每一个用例的接口执行顺序和需要抓取的动态变量
        for case_list in script_case_name_list:#判断处理用例
            print ("##################  执行用例开始  ################## [ %s ]"%str(case_list))
            execution_case = Script_Case_Info.objects.filter(script_case_id=case_list)[0]#获取用例表对象
            config = execution_case.config#获取动态变量值
            parameter_ddt = execution_case.parameter_ddt#获取该用例所有接口需要用到的参数
            parameter_ddt_dict = json.loads(parameter_ddt) #将字符串转字典
            parameter_ddt_list = parameter_ddt_dict.keys()
            print ("参数化接口名list%s" % str(parameter_ddt_list))
            execution_case_oder_list = str(execution_case.execution_order).split('->')#获取单个用例下面的所有接口

            execution_case_oder_dict = {}
            execution_case_oder_list_unique = []  # 需要执行的接口去重
            for unique_list in execution_case_oder_list:
                if unique_list not in execution_case_oder_list_unique:
                    execution_case_oder_list_unique.append(unique_list)
            print (execution_case_oder_list_unique)

            for execution_case_unique in execution_case_oder_list_unique: #用字典保存接口执行的次数
                execution_case_oder_dict[execution_case_unique] = 0

            print (execution_case_oder_dict)

            if '' == config:
                '''
                循环顺序执行接口并返回状态码
                '''
                for list_i_oder in execution_case_oder_list:  # list = Project_Case.case_id 调用接口
                    print ('*********  执行用例['+ str(case_list) +']下的接口 :  ' + str(list_i_oder) + '**********')
                    execution_case_oder_dict[list_i_oder] = execution_case_oder_dict[list_i_oder] + 1 #调用一次接口累加一次

                    print (execution_case_oder_dict)

                    project_case_obj = Project_Case.objects.filter(case_id=list_i_oder)[0]
                    method = project_case_obj.method
                    parameter_format = project_case_obj.parameter_format
                    project_name_id = project_case_obj.project_name_id
                    # 获取项目的domain
                    project_obj = Project.objects.filter(project_name=project_name_id)[0]
                    project_code = project_obj.project_code
                    project_config_obj = Project_Config.objects.filter(project_id_id=project_code)[0]
                    domain = project_config_obj.domain
                    protocol = project_config_obj.protocol

                    url_path = project_case_obj.url_path
                    parameter = project_case_obj.parameter

                    # if parameter_format == "application/json" and '' != parameter:
                    #     parameter = json.loads(parameter)  # unicode转字典

                    expected = project_case_obj.expected
                    headers = project_case_obj.headers


                    #参数替换 包或 headers 和 parameter  expected
                    if list_i_oder in parameter_ddt_list:
                        param_dict = parameter_ddt_dict[list_i_oder]#获取该接口的参数字典
                        param_list = param_dict.keys()
                        #todo  判断是否为空时
                        for param_l in param_list:
                            if "$("+str(param_l)+")" in str(parameter):
                                #print ("parameter=%s" % parameter)
                                #print (execution_case_oder_dict[list_i_oder])
                                #print (param_dict[param_l])
                                if method == "POST" and parameter_format == "application/json" and "\"{" in parameter:
                                    parameter = str(parameter).replace("\"$("+str(param_l)+")\"",param_dict[param_l][execution_case_oder_dict[list_i_oder]-1])
                                else:
                                    parameter = str(parameter).replace("$("+str(param_l)+")",param_dict[param_l][execution_case_oder_dict[list_i_oder]-1])

                            if "$("+str(param_l)+")" in str(headers):
                                headers = str(headers).replace("$("+str(param_l)+")",param_dict[param_l][execution_case_oder_dict[list_i_oder]-1])
                                #print ("headers=%s" % headers)
                                #print (execution_case_oder_dict[list_i_oder])
                            if "$("+str(param_l)+")" in str(url_path):
                                url_path = str(url_path).replace("$("+str(param_l)+")",param_dict[param_l][execution_case_oder_dict[list_i_oder]-1])
                                #print ("url_path=%s" % url_path)
                                #print (execution_case_oder_dict[list_i_oder])
                            if "$("+str(param_l)+")" in str(expected):
                                expected = str(expected).replace("$("+str(param_l)+")",param_dict[param_l][execution_case_oder_dict[list_i_oder]-1])
                                #print ("expected=%s" % expected)
                                #print (execution_case_oder_dict[list_i_oder])

                    print (parameter,url_path,headers,expected)

                    try:
                        api_log = Execute_Interface.execute_interface(project_name=project_name_id,protocol=protocol, method=method,
                                                                            parameter_format=parameter_format,
                                                                            url_path=url_path, parameter=parameter,
                                                                            expected=expected,
                                                                            headers=headers, domain=domain, flag=3,
                                                                            dynamic=None,user_info=userinfo_dict)

                        print ("config为空下收集api执行日志和状态*****************************")
                        print (api_log[0:1500])
                        log_scripts.info("\rreport_id["+report_id+"] ["+str(case_list)+"]用例下的["+str(list_i_oder)+"]接口\r:"+api_log)
                        Mylogging.interface("--------------------------------------------------------------------------\r\n")
                        status = api_log.split('AutoFW test reslut:')[1].split('\'')[0]  # 执行结果
                        print ("config为空下收集api执行日志和状态***************end**************")
                        log_report_id = report_id
                        log_API_id = list_i_oder
                        log_case_id = case_list
                        log_execute_case = api_log[0:1500]
                        status = status
                        execute_case_log_dict = {
                            "log_report_id_id": log_report_id, "log_API_id_id": log_API_id,
                            "log_case_id_id": log_case_id,
                            "log_execute_case": log_execute_case, "status": status, "bak1": "bak1"
                        }

                        Execute_Case_Log.objects.create(**execute_case_log_dict)
                    except:
                        print ("*************["+str(case_list)+"]用例下的["+str(list_i_oder)+"]接口出现异常")
                        print traceback.format_exc()
                        # skipCount += 1
                        status = "SKIP"
                        log_report_id = report_id
                        log_API_id = list_i_oder
                        log_case_id = case_list
                        log_execute_case = str(traceback.format_exc())
                        Mylogging.error("*************["+str(case_list)+"]用例下的["+str(list_i_oder)+"]接口出现异常\r:"+log_execute_case)

                        execute_case_log_dict = {
                            "log_report_id_id": log_report_id, "log_API_id_id": log_API_id,
                            "log_case_id_id": log_case_id,
                            "log_execute_case": log_execute_case, "status": status, "bak1": "bak1"
                        }
                        Execute_Case_Log.objects.create(**execute_case_log_dict)

            else:
                '''
                1:解析config
                    1.1 需要提取动态变量名list    Dynamic_value_list
                    1.2 需要提取动态变量名的接口名    from_interface_list
                    1.3 {需要提取变量接口名:动态变量名}字典    dynamic_from_interface_dict
                    1.4 需要传入变量的接口名list      to_interface_list
                    1.5 {需要传入变量接口名：动态变量名}字典   dynamic_to_interface_dict
                    1.6 {需要传入接口:变量值} null
          
                '''
                config_dict = json.loads(str(config))#把unicode转字典  (暂未校验前端传递config是否为字典 todo)

                Dynamic_value_list = dict(config_dict).keys()#获取该用例的所有需要抓取的动态变量名 1.1
                from_interface_list = []#存储所有需要抓取动态值的接口id 1.2
                dynamic_from_interface_dict = {} #1.3
                to_interface_list = []#存储所有需要传入动态值的接口id 1.4
                dynamic_to_interface_dict = {}#存储需要传入变量接口名与动态变量名 1.5
                to_interface_dynamic_value = {} #存储需要传入接口和变量值  1.6

                print ("--------------------解析config-------start----------------")
                for list_d in Dynamic_value_list:
                    from_case_to_dict = config_dict[list_d] #获取config的values 即动态值时从那个接口抓取，用到那些接口去
                    interface_id = dict(from_case_to_dict).keys()[0] #需要抓取的接口
                    from_interface_list.append(interface_id) # 1.2 #存储需要抓取的接口
                    to_interface_l = from_case_to_dict[interface_id] #获取需要传入动态变量的接口list

                    # to_interface_l = str(to_interface_l[0]).split(',')
                    to_interface_list = to_interface_l #1.4 存储所有需要传入动态值的接口 list
                    for list_i in to_interface_list:
                        dynamic_to_interface_dict[list_i] = list_d #1.5
                    dynamic_from_interface_dict[interface_id] = list_d #1.3

                print ("存储所有需[要抓取]动态值的接口名 list:"+str(from_interface_list))
                print ("存储所有需[要传入]动态值的接口名 list:"+str(to_interface_list))
                print ("-------------------------")
                print ("{需[要抓取]变量接口名:动态变量名}  dict"+str(dynamic_from_interface_dict))
                print ("{需[要传入]变量接口名:动态变量名}  dict"+str(dynamic_to_interface_dict))
                print (str(case_list)+" 用例下面的所有接口:"+str(execution_case_oder_list))
                print ("--------------------解析config-------end----------------")

                for list_i_oder in execution_case_oder_list:#list = Project_Case.case_id 调用接口
                    print ("execute_interface_order:  "+str(list_i_oder))
                    print ('*********  执行接口组[' + str(execution_case_oder_list) + ']下的接口 :  ' + str(list_i_oder) + '**********')
                    '''
                    1:获取list的mothod/parameter_format 判断接口执行分支
                    2:判断动态变量是否需要抓取
                        2.1：是 抓取 判断动态变量抓取的接口是否时当前list接口
                            2.1.1：是 抓取并传出值
                            2.1.2：否 跳过抓取过程
                        2.2：否 不抓取
                    3：执行接口，收集接口执行过程日志
                    4：返回接口执行状态
                    '''
                    project_case_obj = Project_Case.objects.filter(case_id=list_i_oder)[0]
                    method = project_case_obj.method
                    parameter_format = project_case_obj.parameter_format
                    project_name_id = project_case_obj.project_name_id
                    #获取项目的domain
                    project_obj = Project.objects.filter(project_name=project_name_id)[0]
                    project_code = project_obj.project_code
                    project_config_obj = Project_Config.objects.filter(project_id_id=project_code)[0]
                    domain = project_config_obj.domain
                    protocol = project_config_obj.protocol

                    url_path = project_case_obj.url_path
                    parameter = project_case_obj.parameter

                    # if parameter_format == "application/json" and '' != parameter:
                    #     parameter = json.loads(parameter)#unicode转字典

                    expected = project_case_obj.expected
                    headers = project_case_obj.headers

                    # 参数替换 包或 headers 和 parameter  expected
                    if list_i_oder in parameter_ddt_list:
                        param_dict = parameter_ddt_dict[list_i_oder]  # 获取该接口的参数字典
                        param_list = param_dict.keys()
                        # todo  判断是否为空时
                        for param_l in param_list:
                            if "$(" + str(param_l) + ")" in str(parameter):
                                # print ("parameter=%s" % parameter)
                                # print (execution_case_oder_dict[list_i_oder])
                                # print (param_dict[param_l])
                                if method == "POST" and parameter_format == "application/json" and "\"{" in parameter:
                                    parameter = str(parameter).replace("\"$(" + str(param_l) + ")\"",
                                                                       param_dict[param_l][
                                                                           execution_case_oder_dict[list_i_oder] - 1])
                                else:
                                    parameter = str(parameter).replace("$(" + str(param_l) + ")", param_dict[param_l][
                                        execution_case_oder_dict[list_i_oder] - 1])

                            if "$(" + str(param_l) + ")" in str(headers):
                                headers = str(headers).replace("$(" + str(param_l) + ")", param_dict[param_l][
                                    execution_case_oder_dict[list_i_oder] - 1])
                                # print ("headers=%s" % headers)
                                # print (execution_case_oder_dict[list_i_oder])
                            if "$(" + str(param_l) + ")" in str(url_path):
                                url_path = str(url_path).replace("$(" + str(param_l) + ")", param_dict[param_l][
                                    execution_case_oder_dict[list_i_oder] - 1])
                                # print ("url_path=%s" % url_path)
                                # print (execution_case_oder_dict[list_i_oder])
                            if "$(" + str(param_l) + ")" in str(expected):
                                expected = str(expected).replace("$(" + str(param_l) + ")", param_dict[param_l][
                                    execution_case_oder_dict[list_i_oder] - 1])
                                # print ("expected=%s" % expected)
                                # print (execution_case_oder_dict[list_i_oder])

                    print (parameter, url_path, headers, expected)


                    if list_i_oder in from_interface_list and list_i_oder not in to_interface_list:#接口在需要提取动态变量名list中
                        print ("执行接口分支 只需要抓取动态变量的接口%s" % str(list_i_oder))
                        dynamic_name = dynamic_from_interface_dict[list_i_oder]#获取动态变量名
                        to_interfaces = []#通过value获取key值 存储需要传入动态变量的接口
                        for k,v in dynamic_to_interface_dict.items():
                            if v == dynamic_name:
                                to_interfaces.append(k)

                        dynamic_values_from_dict = {list_i_oder:dynamic_name}
                        # print ("需要抓取动态变量的接口：抓取的动态变量名--------------%s"%dynamic_values_from_dict)
                        # print ("需要传入该动态变量名的接口列表--------------%s"%str(to_interfaces))

                        print ("×××××start×××××××开始调用接口执行引擎××××××××××××××××参数如下：")
                        print ("protocol：[ "+str(protocol)+" ]*************数据类型：[ "+str(type(protocol))+" ]")
                        print ("method：[ "+str(method) + " ]***************数据类型：[ " + str(type(method))+" ]")
                        print ("parameter_format：[ "+str(parameter_format) + " ]***************数据类型：[ " + str(type(parameter_format))+" ]")
                        print ("url_path：[ "+str(url_path) + " ]***************数据类型：[ " + str(type(url_path))+" ]")
                        print ("parameter：[ "+str(parameter) + " ]***************数据类型：[ " + str(type(parameter))+" ]")
                        print ("expected：[ "+str(expected) + " ]***************数据类型：[ " + str(type(expected))+" ]")
                        print ("headers：[ "+str(headers) + " ]***************数据类型：[ " + str(type(headers))+" ]")
                        print ("domain：[ "+str(domain) + " ]***************数据类型：[ " + str(type(domain))+" ]")
                        print ("{需抓变量的接口：变量名 的字典}：[ "+str(dynamic_values_from_dict) + " ]***************数据类型：[ " + str(type(dynamic_values_from_dict))+" ]")

                        try:
                            dynamic_value,api_log = Execute_Interface.execute_interface(project_name=project_name_id,protocol=protocol,method=method,parameter_format=parameter_format,
                                                               url_path=url_path,parameter=parameter,expected=expected,
                                                               headers=headers,domain=domain,flag=1,dynamic=dynamic_values_from_dict,user_info=userinfo_dict)#执行接口 返回执行结果
                            print ("执行接口后返回需要抓取动态变量值：%s"%str(dynamic_value))
                            print ("执行接口后返回执行结果集：%s"%str(api_log))
                            log_scripts.info("\rreport_id["+report_id+"] [" + str(case_list) + "]用例下的[" + str(list_i_oder) + "]接口\r:" + api_log)
                            Mylogging.interface("--------------------------------------------------------------------------\r\n")
                            print ("×××××end×××××××开始调用接口执行引擎××××××××××××××××")
                            for list_to_i in to_interfaces:
                                to_interface_dynamic_value[list_to_i] = dynamic_value#{需要传入动态变量的接口：动态变量值} 1.6
                        except:
                            print ("*************[" + str(case_list) + "]用例下的[" + str(list_i_oder) + "]接口出现异常")
                            print traceback.format_exc()
                            dynamic_value, api_log = "Exception" , str(traceback.format_exc())
                            Mylogging.error(api_log)
                            for list_to_i in to_interfaces:
                                to_interface_dynamic_value[list_to_i] = dynamic_value#{需要传入动态变量的接口：动态变量值} 1.6
                            print ("×××××end×××××××开始调用接口执行引擎××××××××××××××××")

                    elif list_i_oder in to_interface_list and list_i_oder not in from_interface_list:#接口在需要传入动态变量名list中
                        print ("执行接口分支 只需要传入动态变量的接口%s" % str(list_i_oder))
                        dynamic_value = to_interface_dynamic_value[list_i_oder]
                        dynameic_name = dynamic_to_interface_dict[list_i_oder]
                        dynamic_dict = {dynameic_name:dynamic_value}

                        print ("×××××start×××××××开始调用接口执行引擎××××××××××××××××参数如下：")
                        print ("protocol：[ " + str(protocol) + " ]*************数据类型：[ " + str(type(protocol)) + " ]")
                        print ("method：[ " + str(method) + " ]***************数据类型：[ " + str(type(method)) + " ]")
                        print ("parameter_format：[ " + str(parameter_format) + " ]***************数据类型：[ " + str(type(parameter_format)) + " ]")
                        print ("url_path：[ " + str(url_path) + " ]***************数据类型：[ " + str(type(url_path)) + " ]")
                        print ("parameter：[ " + str(parameter) + " ]***************数据类型：[ " + str(type(parameter)) + " ]")
                        print ("expected：[ " + str(expected) + " ]***************数据类型：[ " + str(type(expected)) + " ]")
                        print ("headers：[ " + str(headers) + " ]***************数据类型：[ " + str(type(headers)) + " ]")
                        print ("domain：[ " + str(domain) + " ]***************数据类型：[ " + str(type(domain)) + " ]")
                        print ("{需传入变量的接口：变量值 的字典}：[ " + str(dynamic_dict) + " ]***************数据类型：[ " + str(type(dynamic_dict)) + " ]")

                        try:
                            api_log = Execute_Interface.execute_interface(project_name=project_name_id,protocol=protocol,method=method,parameter_format=parameter_format,
                                                               url_path=url_path,parameter=parameter,expected=expected,
                                                               headers=headers,domain=domain,flag=2,
                                                              dynamic=dynamic_dict,user_info=userinfo_dict)  # 执行接口

                            print ("执行接口后返回执行结果集：%s" % str(api_log))
                            log_scripts.info("\rreport_id["+report_id+"] [" + str(case_list) + "]用例下的[" + str(list_i_oder) + "]接口\r:" + api_log)
                            Mylogging.interface("--------------------------------------------------------------------------\r\n")
                            print ("×××××end×××××××开始调用接口执行引擎××××××××××××××××")
                        except:
                            print ("*************[" + str(case_list) + "]用例下的[" + str(list_i_oder) + "]接口出现异常")
                            print traceback.format_exc()
                            api_log = str(traceback.format_exc())
                            Mylogging.error(api_log)
                            print ("×××××end×××××××开始调用接口执行引擎××××××××××××××××")


                    elif list_i_oder in from_interface_list and list_i_oder in to_interface_list:
                        print ("执行接口分支 需要传入动态变量值又需要抓取动态变量的接口%s"%str(list_i_oder))
                        #先传入在抓取
                        dynamic_value = to_interface_dynamic_value[list_i_oder]
                        dynameic_name = dynamic_to_interface_dict[list_i_oder]
                        dynamic_dict = {dynameic_name: dynamic_value}

                        print ("×××××start×××××××开始调用接口执行引擎××××××××××××××××参数如下：")
                        print ("protocol：[ " + str(protocol) + " ]*************数据类型：[ " + str(type(protocol)) + " ]")
                        print ("method：[ " + str(method) + " ]***************数据类型：[ " + str(type(method)) + " ]")
                        print ("parameter_format：[ " + str(parameter_format) + " ]***************数据类型：[ " + str(type(parameter_format)) + " ]")
                        print ("url_path：[ " + str(url_path) + " ]***************数据类型：[ " + str(type(url_path)) + " ]")
                        print ("parameter：[ " + str(parameter) + " ]***************数据类型：[ " + str(type(parameter)) + " ]")
                        print ("expected：[ " + str(expected) + " ]***************数据类型：[ " + str(type(expected)) + " ]")
                        print ("headers：[ " + str(headers) + " ]***************数据类型：[ " + str(type(headers)) + " ]")
                        print ("domain：[ " + str(domain) + " ]***************数据类型：[ " + str(type(domain)) + " ]")
                        print ("{需传入变量的接口：变量值 的字典}：[ " + str(dynamic_dict) + " ]***************数据类型：[ " + str(type(dynamic_dict)) + " ]")

                        print ("先传入变量:"+str(dynamic_dict))
                        try:
                            api_log = Execute_Interface.execute_interface(project_name=project_name_id,protocol=protocol, method=method,
                                                                            parameter_format=parameter_format,
                                                                            url_path=url_path, parameter=parameter,
                                                                            expected=expected,
                                                                            headers=headers, domain=domain, flag=2,
                                                                            dynamic=dynamic_dict,user_info=userinfo_dict)  # 执行接口

                            print ("执行接口后返回执行结果集：%s" % str(api_log))
                            log_scripts.info("\rreport_id["+report_id+"] [" + str(case_list) + "]用例下的[" + str(list_i_oder) + "]接口\r:" + api_log)
                            Mylogging.interface("--------------------------------------------------------------------------\r\n")
                            print ("×××××end×××××××开始调用接口执行引擎××××××××××××××××")
                        except:
                            print ("*************[" + str(case_list) + "]用例下的[" + str(list_i_oder) + "]接口出现异常")
                            print traceback.format_exc()
                            api_log = str(traceback.format_exc())
                            Mylogging.error(api_log)
                            print ("×××××end×××××××开始调用接口执行引擎××××××××××××××××")

                        #再抓取
                        dynamic_name = dynamic_from_interface_dict[list_i_oder]  # 获取动态变量名

                        to_interfaces = []  # 通过value获取key值 存储需要传入动态变量的接口
                        for k, v in dynamic_to_interface_dict.items():
                            if v == dynamic_name:
                                to_interfaces.append(k)

                        dynamic_values_from_dict = {list_i_oder: dynamic_name}

                        print ("后抓取变量:"+str(dynamic_values_from_dict))
                        try:
                            dynamic_value,api_log = Execute_Interface.execute_interface(project_name=project_name_id,protocol=protocol, method=method,
                                                                                parameter_format=parameter_format,
                                                                                url_path=url_path, parameter=parameter,
                                                                                expected=expected,
                                                                                headers=headers, domain=domain, flag=1,
                                                                                dynamic=dynamic_values_from_dict,user_info=userinfo_dict)  # 执行接口 返回执行结果
                            print ("执行接口后返回需要抓取动态变量值：%s" % dynamic_value)
                            print ("执行接口后返回执行结果集：%s" % str(api_log))
                            log_scripts.info("\rreport_id["+report_id+"] [" + str(case_list) + "]用例下的[" + str(list_i_oder) + "]接口\r:" + api_log)
                            Mylogging.interface("--------------------------------------------------------------------------\r\n")
                            print ("×××××end×××××××开始调用接口执行引擎××××××××××××××××")

                            for list_to_i in to_interfaces:
                                to_interface_dynamic_value[list_to_i] = dynamic_value  # {需要传入动态变量的接口：动态变量值} 1.6
                        except:
                            print ("*************[" + str(case_list) + "]用例下的[" + str(list_i_oder) + "]接口出现异常")
                            print traceback.format_exc()
                            dynamic_value,api_log = "Exception",str(traceback.format_exc())
                            Mylogging.error(api_log)
                            for list_to_i in to_interfaces:
                                to_interface_dynamic_value[list_to_i] = dynamic_value  # {需要传入动态变量的接口：动态变量值} 1.6
                            print ("×××××end×××××××开始调用接口执行引擎××××××××××××××××")


                    else:#接口不需要提取或者传入动态变量
                        print ("执行接口分支 不需要抓取和传入动态变量的接口%s" % str(list_i_oder))

                        print ("×××××start×××××××开始调用接口执行引擎××××××××××××××××参数如下：")
                        print ("protocol：[ " + str(protocol) + " ]*************数据类型：[ " + str(type(protocol)) + " ]")
                        print ("method：[ " + str(method) + " ]***************数据类型：[ " + str(type(method)) + " ]")
                        print ("parameter_format：[ " + str(parameter_format) + " ]***************数据类型：[ " + str(type(parameter_format)) + " ]")
                        print ("url_path：[ " + str(url_path) + " ]***************数据类型：[ " + str(type(url_path)) + " ]")
                        print ("parameter：[ " + str(parameter) + " ]***************数据类型：[ " + str(type(parameter)) + " ]")
                        print ("expected：[ " + str(expected) + " ]***************数据类型：[ " + str(type(expected)) + " ]")
                        print ("headers：[ " + str(headers) + " ]***************数据类型：[ " + str(type(headers)) + " ]")
                        print ("domain：[ " + str(domain) + " ]***************数据类型：[ " + str(type(domain)) + " ]")
                        print ("dynamic_dict：[  None  ]********不需要抓取和传入*******数据类型：[ None ]")

                        try:
                            api_log = Execute_Interface.execute_interface(project_name=project_name_id,protocol=protocol,method=method, parameter_format=parameter_format,
                                                              url_path=url_path, parameter=parameter, expected=expected,
                                                              headers=headers, domain=domain, flag=3,
                                                              dynamic=None,user_info=userinfo_dict)  # 执行接口
                            print ("执行接口后返回执行结果集：%s" % str(api_log))
                            log_scripts.info("\rreport_id["+report_id+"] [" + str(case_list) + "]用例下的[" + str(list_i_oder) + "]接口\r:" + api_log)
                            Mylogging.interface("--------------------------------------------------------------------------\r\n")
                            print ("×××××end×××××××开始调用接口执行引擎××××××××××××××××")
                        except:
                            print ("*************[" + str(case_list) + "]用例下的[" + str(list_i_oder) + "]接口出现异常")
                            print traceback.format_exc()
                            api_log = str(traceback.format_exc())
                            Mylogging.error(api_log)
                            print ("×××××end×××××××开始调用接口执行引擎××××××××××××××××")

                    '''
                    list_i_oder case into table
                    1：返回case执行log和状态，存储数据
                    '''
                    print ("************api_log[0:9] =***************")
                    print (api_log[0:9])
                    if api_log[0:9] != "Traceback":
                        print ("config非空下收集api执行日志和状态***************start**************")
                        print (api_log[0:1500])
                        status = api_log.split('AutoFW test reslut:')[1].split('\'')[0]#执行结果
                        print ("config非空下收集api执行日志和状态***************end**************")
                        log_report_id = report_id
                        log_API_id = list_i_oder
                        log_case_id = case_list
                        log_execute_case = api_log[0:1500]
                        status = status
                        execute_case_log_dict = {
                            "log_report_id_id": log_report_id, "log_API_id_id": log_API_id, "log_case_id_id": log_case_id,
                            "log_execute_case": log_execute_case, "status": status,"bak1":"bak1"
                        }

                        Execute_Case_Log.objects.create(**execute_case_log_dict)
                    else:
                        status = "SKIP"
                        log_report_id = report_id
                        log_API_id = list_i_oder
                        log_case_id = case_list
                        log_execute_case = api_log
                        execute_case_log_dict = {
                            "log_report_id_id": log_report_id, "log_API_id_id": log_API_id,
                            "log_case_id_id": log_case_id,
                            "log_execute_case": log_execute_case, "status": status, "bak1": "bak1"
                        }
                        Mylogging.error("*************["+str(case_list)+"]用例下的["+str(list_i_oder)+"]接口出现异常\r:"+log_execute_case)

                        Execute_Case_Log.objects.create(**execute_case_log_dict)
        # except:
        #     traceback.print_exc()
            #return JsonResponse({"status":"failed","msg":"出现异常，执行用例失败"})

        total_interface = Execute_Case_Log.objects.filter(log_report_id_id=report_id).count()#总接口个数
        total_case = len(script_case_name_list) #总用例个数
        fail_count = 0
        skip_count = 0
        for case_l in script_case_name_list:
            count_f = Execute_Case_Log.objects.filter(log_report_id_id=report_id,log_case_id_id=case_l,status="FAILED").count()#用例是否failed
            count_s = Execute_Case_Log.objects.filter(log_report_id_id=report_id,log_case_id_id=case_l,status="SKIP").count()#用例是否failed

            if count_f > 0:
                fail_count += 1
            if count_s > 0:
                skip_count += 1
        pass_count = len(script_case_name_list) - fail_count - skip_count
        # pass_total = Execute_Case_Log.objects.filter(log_report_id_id=report_id,status="PASS").count()
        # fail_total = Execute_Case_Log.objects.filter(log_report_id_id=report_id, status="FAILED").count()
        # skip_total = total_case - pass_total - fail_total

        Case_Execution_Report.objects.filter(report_id=report_id).update(pass_total=pass_count,fail_total=fail_count
                                                                         ,skip_total=skip_count)

        # -------start-------发送测试报告邮件---------------------
        execute_time = execute_time.strftime("%Y%m%d%H%M%S")
        emp_obj_list = Emp_Info.objects.filter(user_id_id=username)  # 主键，只有一条数据
        if send_email_flag == "yes":
            if emp_obj_list.exists():
                email_adr_list = []
                for list in emp_obj_list:
                    emails = list.email
                    email_adr_list.append(emails)
                send_mail(report_name, username, execute_time, str(total_case), str(pass_count), str(fail_count),
                          str(skip_count), email_adr_list)
                content = {"status":"success","msg":"用例执行成功，邮件已发！"}
            else:
                content = {"status": "success", "msg": "用例执行成功，邮件发送失败，该用户没有邮箱信息！"}

            return JsonResponse(content)
                # -------end-------发送测试报告邮件---------------------

        return JsonResponse({"status":"success","msg":"用例执行成功"})


#删除测试用例
def delete_test_case(request):
    print ("delete_test_case")
    if request.method == "GET":
        script_case_name_json = request.GET.get("script_case_name_json")
        username = request.GET.get("username")

        script_case_name_list = str(script_case_name_json).split(',')
        script_case_name_list.remove('')  # 移除最后一个空元素

        for list in script_case_name_list:
            log_case_id_count = Execute_Case_Log.objects.filter(log_case_id_id=list).count()
            if log_case_id_count > 0:
                return JsonResponse({"status":"failed","msg":str(list)+"用例已经执行过并生成测试日志和报告，暂不能删除[本次删除失败]"})

        for list in script_case_name_list:
            Script_Case_Info.objects.filter(script_case_id=list).delete()#删除用例
        msg = "删除成功，一共删除了%s"%str(len(script_case_name_list))+"个用例"
        return JsonResponse({"status": "success", "msg": msg})

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

def display(request):
    return render(request, 'AutoFW/display.html')

# @accept_websocket
# def echo(request):
#     if not request.is_websocket():#判断是不是websocket连接
#         try:#如果是普通的http方法
#             message = request.GET['message']
#             return HttpResponse(message)
#         except:
#             return render(request,'AutoFW/echo.html')
#     else:
#         for message in request.websocket:
#             request.websocket.send(message)#发送消息到客户端


#接口报告页面
def report_page(request,username):
    print ("report_page")
    execute_man = UserInfo.objects.values("username")

    content = {"execute_man_list": execute_man, "username": username}
    return render(request, "AutoFW/report_page.html", content)

#用例报告页面
def case_report_page(request,username):
    print ("case_report_page")
    execute_man = UserInfo.objects.values("username")

    content = {"execute_man_list": execute_man, "username": username}
    return render(request, "AutoFW/case_report_page.html", content)


#查询接口列表
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

#查询用例列表
def case_search_report_list(request):
    print ("search_report_list")
    if request.method == "GET":
        report_name = request.GET.get("report_name")
        execute_man = request.GET.get("execute_man")

        # 存放给前端table用的报告数据
        case_report_obj_list = []
        if(execute_man == "" and report_name == ""):
            content = {"status": "case_search_report_list failed ,gei me a condition"}
            return JsonResponse(content)
        elif execute_man == "":
            case_execute_report_obj = Case_Execution_Report.objects.filter(report_name__contains=report_name)

            for list in case_execute_report_obj:
                execute_time_tmp = list.execute_time  # 该批次执行时间点
                execute_time = execute_time_tmp.strftime('%Y-%m-%d')  # 将datatime转成str
                data = {
                    "report_id": list.report_id, "case_total": list.case_total,
                    "pass_total": list.pass_total, "fail_total": list.fail_total,
                    "skip_total": list.skip_total, "execute_man": list.execute_man,
                    "execute_time":execute_time,"report_name":list.report_name
                }
                case_report_obj_list.append(data)

            content = {"status": "success", "case_report_list": case_report_obj_list}
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
            case_execute_report_obj = Case_Execution_Report.objects.filter(execute_man=execute_man)

            for list in case_execute_report_obj:
                execute_time_tmp = list.execute_time  # 该批次执行时间点
                execute_time = execute_time_tmp.strftime('%Y-%m-%d')  # 将datatime转成str
                data = {
                    "report_id": list.report_id, "case_total": list.case_total,
                    "pass_total": list.pass_total, "fail_total": list.fail_total,
                    "skip_total": list.skip_total, "execute_man": list.execute_man,
                    "execute_time":execute_time,"report_name":list.report_name
                }
                case_report_obj_list.append(data)

            content = {"status": "success", "case_report_list": case_report_obj_list}

            return JsonResponse(content)
        else:#执行人和报告名都不为空时
            case_execute_report_obj = Case_Execution_Report.objects.filter(report_name__contains=report_name,execute_man=execute_man)
            for list in case_execute_report_obj:
                execute_time_tmp = list.execute_time  # 该批次执行时间点
                execute_time = execute_time_tmp.strftime('%Y-%m-%d')  # 将datatime转成str
                data = {
                    "report_id": list.report_id, "case_total": list.case_total,
                    "pass_total": list.pass_total, "fail_total": list.fail_total,
                    "skip_total": list.skip_total, "execute_man": list.execute_man,
                    "execute_time":execute_time,"report_name":list.report_name
                }
                case_report_obj_list.append(data)

            content = {"status": "success", "case_report_list": case_report_obj_list}

            return JsonResponse(content)

    return JsonResponse({"status":"failed"})


#查看测试用例报告
def search_case_execute_log_list(request):
    print (search_case_execute_log_list)

    if request.method == "GET":
        report_id = request.GET.get("report_id")
        case_list = []
        execute_case_Log_objs = Execute_Case_Log.objects.filter(log_report_id_id=report_id)
        for list in execute_case_Log_objs:
            if list.log_case_id_id not in case_list:
                case_list.append(list.log_case_id_id)
        # print ("******************")
        # print (case_list)

        report_case_execute_obj_list = []

        for case_l in case_list:
            execute_case_objs = Execute_Case_Log.objects.filter(log_case_id_id=case_l,log_report_id_id=report_id)
            print (case_l)
            for l in execute_case_objs:

                flags = 2  # 2表用例接口中有失败的

                if l.status == "FAILED":
                    # flags = 2  # 1表用例接口存在失败的
                    data_log = {
                        'log_case_id': l.log_case_id_id,
                        'log_report_id':l.log_report_id_id,
                        'states': "FAILED"
                    }
                    report_case_execute_obj_list.append(data_log)
                    # print ("failed break ***********")
                    break
                elif l.status == "SKIP":
                    # flags = 2  # 1表用例接口存在失败的
                    data_log = {
                        'log_case_id': l.log_case_id_id,
                        'log_report_id': l.log_report_id_id,
                        'states': "SKIP"
                    }
                    report_case_execute_obj_list.append(data_log)
                    # print ("skip break ***********")
                    break
                flags = 1    # 1表用例所有接口都是成功的
                # print ("---------------%d"%l.id)
                qs_count = len(execute_case_objs) - 1
                # print (execute_case_objs[qs_count].id)

                if flags == 1 and l.id == execute_case_objs[qs_count].id:#遍历到最后一个元素且都没有失败和跳过的接口
                    print ("执行pass×××××××××××")
                    data_log = {
                        'log_case_id': l.log_case_id_id,
                        'log_report_id': l.log_report_id_id,
                        'states': "PASS"
                    }
                    report_case_execute_obj_list.append(data_log)


        case_execution_report_objs = Case_Execution_Report.objects.filter(report_id=report_id)[0]
        execute_time_tmp = case_execution_report_objs.execute_time  # 该批次执行时间点
        execute_time = execute_time_tmp.strftime('%Y-%m-%d')  # 将datatime转成str
        content = {
            "status": "success", "case_total": case_execution_report_objs.case_total, "report_name": case_execution_report_objs.report_name,
            "pass_total": case_execution_report_objs.pass_total, "fail_total": case_execution_report_objs.fail_total,
            "skip_total": case_execution_report_objs.skip_total, "execute_man": case_execution_report_objs.execute_man,
            "execute_time": execute_time, "report_case_execute_obj_list": report_case_execute_obj_list
        }
        print (report_case_execute_obj_list)

        return JsonResponse(content)


#report 点击查看用例详细报告
def search_case_report_detail_list(request):
    print ("search_case_report_detail_list")
    if request.method == "GET":
        log_case_id_report_id = request.GET.get("log_case_id_report_id")
        log_case_id_report_id_list = str(log_case_id_report_id).split(',')
        log_case_id = log_case_id_report_id_list[0] #用例ID
        log_report_id = log_case_id_report_id_list[1]#报告ID

        execute_case_log_objs = Execute_Case_Log.objects.filter(log_report_id_id=log_report_id,log_case_id_id=log_case_id)
        case_execute_log = []
        for qs in execute_case_log_objs:
            api_id = qs.log_API_id_id
            api_log = qs.log_execute_case
            api_status = qs.status

            data = {
                "api_id":api_id,
                "api_log":api_log,
                "api_status":api_status
            }
            case_execute_log.append(data)

        print (case_execute_log)

        content = {
            "case_detail":case_execute_log
        }
        return JsonResponse(content)


#删除报告
def delete_case_report_from_list(request):
    print ("delete_case_report_from_list")

    if request.method == "GET":
        report_id = request.GET.get("report_id")
        username = request.GET.get("username")
        # TODO 根据权限限制删除
        authority = UserInfo.objects.filter(username=username)[0].authority  # 获取该用户的权限等级
        if "superman" == authority or "primary" == authority:
            Execute_Case_Log.objects.filter(log_report_id_id=report_id).delete()
            Case_Execution_Report.objects.filter(report_id=report_id).delete()
            content = {"status":"success","msg":"删除报告成功"}
            return JsonResponse(content)
        elif "secend" == authority:
            content = {"status": "permission"}
            return JsonResponse(content)
        else:
            content = {"status": "error"}
            return JsonResponse(content)



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
        flags = request.GET.get("flags")

        if "interface" == str(flags):
            batch_report_obj = Batch_Report.objects.filter(report_id=report_id)[0]  # 只能获取一条数据，因为report_id为主键
            execute_time_tmp = batch_report_obj.execute_time  # 该批次执行时间点
            execute_time = execute_time_tmp.strftime('%Y-%m-%d')  # 将datatime转成str
            total = batch_report_obj.API_total
            report_name = batch_report_obj.report_name
            pass_total = batch_report_obj.pass_total
            fail_total = batch_report_obj.fail_total
            skip_total = batch_report_obj.skip_total
            execute_man = batch_report_obj.execute_man
        elif "case" == str(flags):
            case_report_obj = Case_Execution_Report.objects.filter(report_id=report_id)[0]
            execute_time_tmp = case_report_obj.execute_time  # 该批次执行时间点
            execute_time = execute_time_tmp.strftime('%Y-%m-%d')  # 将datatime转成str
            total = case_report_obj.case_total
            report_name = case_report_obj.report_name
            pass_total = case_report_obj.pass_total
            fail_total = case_report_obj.fail_total
            skip_total = case_report_obj.skip_total
            execute_man = case_report_obj.execute_man

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
            result = send_mail(report_name=str(report_name),execute_man=str(execute_man),execute_time=str(execute_time),case_total=str(total),
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
                response_expected_actual_value = rs.split('response_expected_actual_value')[1][1:1500]
                # log_scripts.info(list + ":PASS:" + " pass message [" + rs.split('PASS')[1] + "]")#响应信息都打印
                log_scripts.info(
                    API_name + ":PASS:[time_consuming:" + time_consuming + "]{ response :  "+response_expected_actual_value)  # 只打印成功关键字段

                execute_script_log = str(
                    API_name) + ":<PASS> [time_consuming:" + time_consuming + "]{ response : "+response_expected_actual_value

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
        Mylogging.error("[" + str(API_name) + "] :" + "未获取脚本执行状态，脚本执行失败\r" + rs)
        log_scripts.error(API_name + ":FAILED:" + " error message [ 未获取脚本执行状态，脚本执行失败 ] \r" + rs)

        execute_script_log = str(API_name) + ":<FAILED> " + " error message [脚本运行异常:请查看error.log] \r" + rs[1:1500]
        # 写入Execute_Script_Log表
        dic = {"log_report_id_id": report_id, "log_api_name": str(API_name),
               "log_execute_script": execute_script_log, "status": "skip", "bak1": "bak"}
        Execute_Script_Log.objects.create(**dic)
        skipCount += 1
        # except AttributeError,e:
        #     dict = {"script_status": "NONE"}
        #     Mylogging.error("[" + str(list) + "] :" + "index error,未获取脚本执行状态，脚本执行失败"+e.args)
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


#导入文件生成测试用例
def upload_file(request):
    if request.method == "POST":
        print ("upload_file")
        ret = {'status': "failed", 'msg':"还未开始上传"}
        try:
            uploadFile = request.FILES.get('uploadFile')
            print uploadFile

            f = open(os.path.join('static/upload/case/', uploadFile.name), 'wb')
            for chunk in uploadFile.chunks(chunk_size=1024):
                f.write(chunk)
            ret['status'] = "success"
            ret['msg'] = str(uploadFile.name)+":上传和生成用例成功"
        except Exception as e:
            ret['status'] = "failed"
            ret['msg'] = e
            traceback.format_exc()

        finally:
            f.close()

            if ret['status'] == "success":
                print ("读取excel")
                demo_path = 'static/upload/case/'+str(uploadFile.name)
                xlrd.Book.encoding = "utf-8"
                book = xlrd.open_workbook(demo_path)  # 得到Excel文件的book对象，实例化对象
                try:
                    sheet0 = book.sheet_by_name("OG-AutoFW-CASE")  # 通过sheet索引获得sheet对象
                except Exception,e:
                    ret['status'] = 'errorFile'
                    ret['msg'] = "上传的文件内容格式不对，请下载最新模板"
                    return JsonResponse(ret)

                nrows = sheet0.nrows  # 获取行总数
                E_script_case_id_list = sheet0.col_values(0, 2)  # 获取第一列 从第三行开始获取
                E_script_case_name_list = sheet0.col_values(1, 2)
                script_case_id_c = Script_Case_Info.objects.filter(script_case_id__in=E_script_case_id_list)
                script_case_name_c = Script_Case_Info.objects.filter(script_case_name__in=E_script_case_name_list)
                script_case_id_list = []
                script_case_name_list = []

                # 插入数据前检查唯一键
                if script_case_id_c.count() != 0 and script_case_name_c.count() != 0:
                    ret['status'] = 'blockOut'
                    for l_script_case_id in script_case_id_c:
                        script_case_id_list.append(l_script_case_id.script_case_id)

                    for l_script_case_name in script_case_name_c:
                        script_case_name_list.append(l_script_case_name.script_case_name)

                    ret['msg'] = "接口id和接口名称违反唯一值:case_id[" + str(script_case_id_list) + "] case_name[" + str(
                        script_case_name_list) + "]"
                    return JsonResponse(ret)

                # 循环打印每一行的内容
                for i in range(nrows-2):
                    case_dict = {}
                    case_list = sheet0.row_values(i+2)

                    case_dict['script_case_id'] = str(case_list[0])
                    case_dict['script_case_name'] = str(case_list[1])
                    case_dict['script_case_project_name_id'] = str(case_list[2])
                    case_dict['script_case_module_name_id'] = str(case_list[3])
                    case_dict['execution_order'] = str(case_list[4])
                    case_dict['parameter_ddt'] = str(case_list[5])
                    case_dict['config'] = str(case_list[6])
                    case_dict['creator'] = str(case_list[7])
                    case_dict['script_case_type'] = str(case_list[8])
                    case_dict['status'] = str(case_list[9])
                    case_dict['remark'] = str(case_list[10])

                    try:
                        Script_Case_Info.objects.create(**case_dict)
                    except Exception,e:
                        ret['status'] = 'failed'
                        ret['msg'] = "生成用例失败，请检查数据:["+str(case_list[0])+"]"+str(e)
                        return JsonResponse(ret)

            return JsonResponse(ret)

    return render(request, 'AutoFW/yongli_genirate_page.html')


#导入文件并生成接口信息
def upload_interface_file(request):
    if request.method == "POST":
        print ("upload_file")
        ret = {'status': "failed", 'msg':"还未开始上传"}
        try:
            uploadFile = request.FILES.get('uploadFile')
            print uploadFile

            f = open(os.path.join('static/upload/interface/', uploadFile.name), 'wb')
            for chunk in uploadFile.chunks(chunk_size=1024):
                f.write(chunk)
            ret['status'] = "success"
            ret['msg'] = str(uploadFile.name)+":上传和生成接口成功"
        except Exception as e:
            ret['status'] = "failed"
            ret['msg'] = e
            traceback.format_exc()

        finally:
            f.close()

            if ret['status'] == "success":
                print ("读取excel")
                demo_path = 'static/upload/interface/'+str(uploadFile.name)
                xlrd.Book.encoding = "utf-8"
                book = xlrd.open_workbook(demo_path)  # 得到Excel文件的book对象，实例化对象
                try:
                    sheet0 = book.sheet_by_name("OG-AutoFW-API")  # 通过sheet索引获得sheet对象
                except Exception,e:
                    ret['status'] = 'errorFile'
                    ret['msg'] = "上传的文件内容格式不对，请下载最新模板"
                    return JsonResponse(ret)

                nrows = sheet0.nrows  # 获取行总数
                E_case_id_list = sheet0.col_values(0,2)#获取第一列 从第三行开始获取
                E_case_name_list = sheet0.col_values(1,2)
                case_id_c = Project_Case.objects.filter(case_id__in=E_case_id_list)
                case_name_c = Project_Case.objects.filter(case_name__in=E_case_name_list)
                case_id_list = []
                case_name_list = []

                #插入数据前检查唯一键
                if case_id_c.count() != 0 and case_name_c.count() != 0:
                    ret['status'] = 'blockOut'
                    for l_case_id in case_id_c:
                        case_id_list.append(l_case_id.case_id)

                    for l_case_name in case_name_c:
                        case_name_list.append(l_case_name.case_name)

                    ret['msg'] = "接口id和接口名称违反唯一值:case_id["+str(case_id_list)+"] case_name["+str(case_name_list)+"]"
                    return JsonResponse(ret)
                # 循环打印每一行的内容
                for i in range(nrows-2):
                    case_dict = {}
                    case_list = sheet0.row_values(i+2)

                    case_dict['case_id'] = str(case_list[0])
                    case_dict['case_name'] = str(case_list[1])
                    case_dict['project_name_id'] = str(case_list[2])
                    case_dict['module_name_id'] = str(case_list[3])
                    case_dict['url_path'] = str(case_list[4])
                    case_dict['method'] = str(case_list[5])
                    case_dict['headers'] = str(case_list[6])
                    case_dict['parameter_format'] = str(case_list[7])
                    case_dict['parameter'] = str(case_list[8])
                    case_dict['expected'] = str(case_list[9])
                    case_dict['case_type'] = str(case_list[10])
                    case_dict['description'] = str(case_list[11])
                    case_dict['creator'] = str(case_list[12])

                    try:
                        Project_Case.objects.create(**case_dict)
                    except Exception,e:
                        ret['status'] = 'failed'
                        ret['msg'] = "生成接口失败，请检查数据["+str(case_list[0])+"]"+str(e)
                        return JsonResponse(ret)

            return JsonResponse(ret)

    return render(request, 'AutoFW/yongli_genirate_page.html')