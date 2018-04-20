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
    url(r'^project_manage/(.*)$',views.project_manage),
    url(r'^start/(.*)$', views.app_start),
    url(r'^read/$', views.Read_all_project),
    #url(r'^edit/(?P<id>\d+)/(?p<username>.*)', views.Edit_project),
    url(r'^edit/(?P<id>[0-9]+)/(?P<username>.*)', views.Edit_project),

    url(r'^remove/$', views.Remove_US_ID),
    # url(r'^income_project/(?P<project_id>\d+)', views.income_project),
    url(r'^income_project/(?P<project_id>[0-9A-Za-z_]+)/(?P<username>.*)', views.income_project),
    url(r'^project_attribute/', views.project_attribute),
    url(r'^project_globel_config/(.*)', views.project_globel_config),

    url(r'^module_append/', views.module_append),
    url(r'^module_read/(.*)', views.module_Read_all_SQL),
    url(r'^startModule/(.*)$', views.Module_start),
    url(r'^editModule/(.*)/(.*)', views.Edit_Module),
    url(r'^removeModule/$', views.Remove_Module),
    url(r'^case_read/(.*)', views.case_Read_all_SQL),
    url(r'^startAPI/(?P<project_id>[0-9A-Za-z_]+)/(?P<username>.*)', views.API_start),
    # url(r'^workon_tabs_api/(.*)', views.workon_tabs_api),
    url(r'^workon_tabs_api/(?P<project_id>[0-9A-Za-z_]+)/(?P<username>.*)', views.workon_tabs_api),
    url(r'^editAPI/(?P<project_id>[0-9A-Za-z_]+)/(?P<username>.*)', views.editAPI),
    url(r'^removeAPI/$', views.removeAPI),
    url(r'^user_manage/(.*)', views.user_manage),
    url(r'^userinfo_show/(.*)', views.userinfo_show),
    url(r'^add_userinfo/$', views.add_userinfo),
    url(r'^edit_userinfo/(.*)', views.edit_userinfo),
    url(r'^remove_userinfo/(.*)', views.remove_userinfo),
    url(r'^resetPW_userinfo/(.*)', views.resetPW_userinfo),
    url(r'^personal_manage/(.*)', views.personal_manage),
    url(r'^update_emp_info/(.*)', views.update_emp_info),
    url(r'^change_pw/(.*)', views.change_pw),

    url(r'^test_case_genirate_page/(.*)', views.test_case_genirate_page),

    url(r'^select_load_module/(.*)', views.select_load_module),
    url(r'^search_case/$', views.search_case),
    url(r'^chose_all_genritor_test_script/$', views.chose_all_genritor_test_script),
    url(r'^execute_test_script_page/(.*)', views.execute_test_script_page),
    url(r'^search_script/$', views.search_script),
    url(r'^execute_test_script/$', views.execute_test_script),
    url(r'^delete_test_script/$', views.delete_test_script),

    url(r'^script_log_page/(.*)',views.script_log_page),
    url(r'^delete_script_log/$', views.delete_script_log),
    url(r'^error_log_page/(.*)', views.error_log_page),
    url(r'^delete_error_log/$', views.delete_error_log),
    url(r'^report_page/(.*)', views.report_page),
    url(r'^search_report_list/', views.search_report_list),
    url(r'^search_execute_log_list/', views.search_execute_log_list),
    url(r'^delete_report_by_reportID/', views.delete_report_by_reportID),

    url(r'^send_email_by_report_list/', views.send_email_by_report_list),
    url(r'^execute_maoyan_script/', views.execute_maoyan_script),


]
