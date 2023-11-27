from django.shortcuts import render
import boto3
import json
import uuid

# Create your views here.

def index(request):
    return render(request, 'INFOtemp/index.html')

def login(request):
    return render(request, 'login/login.html')

def list(request):
    return render(request, 'list/list.html')
