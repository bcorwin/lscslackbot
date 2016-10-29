from django.shortcuts import render
from django.http import HttpResponse
import datetime

# Create your views here.

def add_app(request):
    html = '<a href="https://slack.com/oauth/authorize?scope=incoming-webhook,commands,bot&client_id=80096221559.96857334885"><img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>'
    return HttpResponse(html)