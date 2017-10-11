#coding=utf-8
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from models import *
import MySQLdb

def login(request):
    return render(request, 'AutoFW/login.html')


def login_handle(request):
    post = request.POST.get
    user = post.get('username')
    passwd = post.get('password')

    users = UserInfo.objects.filter(username=user)

    conn = MySQLdb.connect(host='localhost',port=3306,db='autofw',user='root',passwd='123456',charset='utf8')

    handle = conn.cursor()

    username = handle.execute("select username from AutoFW_userinfo where username='%s'" % user)
    username = handle.fetchall()

    password = handle.execute("select password from AutoFW_userinfo where username='%s'" % user)
    password = handle.fetchall()

    print ("username:"+username+"  password:"+password)

    #判断元组是否为空，空为false
    if(username and password):
        if(username[0][0]==user and password[0][0]==passwd):
            username = username[0][0]
            position = UserInfo.objects.filter(username=username)
            position = position[0][0]

            context = {'username':username,'position':position}

            return render(request,'AutoFW/workbench.html')


    return HttpResponse("hello")