from django.shortcuts import render
import boto3
import json
import uuid

# Create your views here.

def index(request):
    return render(request, 'INFOtemp/index.html')
