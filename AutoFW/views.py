#coding=utf-8
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse


def login(request):
    return render(request, 'AutoFW/index.html')