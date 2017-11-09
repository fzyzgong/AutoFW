"""AutoFWOG URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from . import views


urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^login_handle/$', views.login_handle),
    # url(r'^go_header/$',views.go_header),
    # url(r'^exec_task/$',views.exec_task),
    url(r'^login_check_name/$',views.login_check_name),
    url(r'^login_check_passwd/$', views.login_check_passwd),
    url(r'^project_manage/$',views.project_manage),
    url(r'^start/$', views.app_start),
    url(r'^read/$', views.Read_all_SQL),
    url(r'^edit/(?P<id>\d+)', views.Edit_UserNmae),
    url(r'^remove/$', views.Remove_US_ID),
    # url(r'^income_project/(?P<project_id>\d+)', views.income_project),
    url(r'^income_project/(\d+)', views.income_project),
    url(r'^project_attribute/', views.project_attribute),
    url(r'^module_append/', views.module_append),
    url(r'^module_read/(\d+)', views.module_Read_all_SQL),
    url(r'^startModule/(\d+)$', views.Module_start),
    url(r'^editModule/(.*)/(.*)', views.Edit_Module),
    url(r'^removeModule/$', views.Remove_Module),
    url(r'^case_read/(\d+)', views.case_Read_all_SQL),
    url(r'^startAPI/(\d+)', views.API_start),
    url(r'^workon_tabs_api/(\d+)', views.workon_tabs_api),
    url(r'^editAPI/(\d+)', views.editAPI),
    url(r'^removeAPI/$', views.removeAPI),
    url(r'^user_manage/(.*)', views.user_manage),
    url(r'^userinfo_show/(.*)', views.userinfo_show),
    url(r'^add_userinfo/$', views.add_userinfo),
    url(r'^edit_userinfo/(.*)', views.edit_userinfo),
    url(r'^remove_userinfo/(.*)', views.remove_userinfo),
    url(r'^resetPW_userinfo/(.*)', views.resetPW_userinfo),
    url(r'^personal_manage/(.*)', views.personal_manage),
]
