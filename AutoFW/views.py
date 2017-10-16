#coding=utf-8
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from models import *
import MySQLdb

def login(request):
    return render(request, 'AutoFW/login.html')


def login_check_name(request):
    uname = request.GET.get('username')
    count = UserInfo.objects.filter(username=uname).count()
    return JsonResponse({'count': count})


def login_check_passwd(request):
    upasswd = request.POST.get('password')
    username = request.POST.get('username')
    # s1=sha1()
    # s1.update(upasswd)
    # upasswd = s1.hexdigest()
    count = UserInfo.objects.filter(username=username,password=upasswd).count()
    return JsonResponse({'count':count})


def login_handle(request):
    post = request.POST
    user = post.get('username')
    passwd = post.get('password')

    users = UserInfo.objects.filter(username=user)

    conn = MySQLdb.connect(host='localhost',port=3306,db='autofw',user='root',passwd='123456',charset='utf8')

    handle = conn.cursor()

    username = handle.execute("select username from AutoFW_userinfo where username='%s'" % user)
    username = handle.fetchone()

    password = handle.execute("select password from AutoFW_userinfo where username='%s'" % user)
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

            return render(request,'AutoFW/workbench.html')
        else:
            # return HttpResponse("username or passwd1 error")
            return render(request, 'AutoFW/login.html')
    else:
        # return HttpResponse("username or passwd error")
        return render(request, 'AutoFW/login.html')


#first page
def go_header(request):

    return render(request,'AutoFW/workbench.html')


def exec_task(request):

    return render(request,'AutoFW/exec_task.html')