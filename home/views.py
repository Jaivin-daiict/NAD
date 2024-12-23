from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import UserProfile, Criterion, SubCriterion, Metrics, Document
from django.utils import timezone

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

def index(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('signin')
    
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('metric_') and value:
                metric_id = key.split('_')[1]
                metric = Metrics.objects.get(id=metric_id)
                metric.answer = value
                metric.answered_by = user
                metric.answered_at = timezone.now()
                metric.dataTemplate = request.FILES.get('dataTemplate_metric_' + metric_id, None)
                documentsForm = request.FILES.getlist('file_metric_' + metric_id)
                for documentForm in documentsForm:
                    document = Document(description=documentForm.name, created_by=user, metrics=metric, documentFile=documentForm)
                    document.save()
                metric.save()
        return redirect('index')
    
    if request.method == 'GET':
        firstName = user.first_name
        userProfileObj = UserProfile.objects.get(user=user)
        role = userProfileObj.role
        # # Calculate the remaining time in seconds
        # current_datetime = timezone.now()
        # remaining_time = userProfileObj.end_date.astimezone() - current_datetime 
        # remaining_time_days = remaining_time.days
        # remaining_time_seconds = remaining_time.seconds
        # remaining_time_hours = remaining_time_seconds // 3600
        # remaining_time_minutes = (remaining_time_seconds // 60) % 60
        # remaining_time_seconds = remaining_time_seconds % 60
        # remaining_time = f"{remaining_time_days} days, {remaining_time_hours} hours, {remaining_time_minutes} minutes"
        # remaining_time_seconds = int(remaining_time.total_seconds())
        
        current_time = timezone.now()
        # remaining_time =  current_time - userProfileObj.end_date.astimezone().strftime('%Y-%m-%d %H:%M:%S')
        # remaining_time_seconds = remaining_time
        print(userProfileObj.end_date.astimezone().strftime('%Y-%m-%d %H:%M:%S'))
        remaining_time = userProfileObj.end_date
        metricsList = userProfileObj.metrics.all()
        subCriterionList = []
        criterionList = []

        for metric in metricsList:
            if not any(d['name'] == metric.sub_criterion.criterion.name for d in criterionList):
                criterionList.append({
                    "name": metric.sub_criterion.criterion.name,
                    "criterionId": metric.sub_criterion.criterion.criterionId
                })

        for metric in metricsList:
            if not any(d['name'] == metric.sub_criterion.name for d in subCriterionList):
                subCriterionList.append({
                    "SubCriterionId": metric.sub_criterion.SubCriterionId,
                    "name": metric.sub_criterion.name,
                    "criterion": metric.sub_criterion.criterion.name,
                    "metricList": []
                })
        for metric in metricsList:
            for i in range(len(subCriterionList)):
                if subCriterionList[i]["name"] == metric.sub_criterion.name:
                    documents = Document.objects.filter(metrics=metric)
                    metric.documents = documents
                    subCriterionList[i]["metricList"].append(metric)
        for i in range(len(criterionList)):
            criterionList[i]["subcriterionList"] = []
            for subCriterion in subCriterionList:
                if subCriterion["criterion"] == criterionList[i]["name"]:
                    criterionList[i]["subcriterionList"].append(subCriterion)
        #sort by metrics id
    
        criterionList.sort(key=lambda x: x["criterionId"])
        # criterionList.sort(key=lambda x: x["subcriterionList"])

        # print(criterionList[0]['subcriterionList'][0]['metricList'][0],criterionList[0]['subcriterionList'][0]['metricList'][0].dataTemplate)
        context = {
            'name': firstName,
            'role': role,
            'remaingtime':remaining_time,
            'criterionList': criterionList
        }
        return render(request, "home.html", context)

@csrf_exempt
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return redirect('signin')
    return render(request, "login.html")

def signout(request):
    logout(request)
    return redirect('signin')


def addUser(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    if userProfile.role != 'admin':
        return redirect('index')
    if request.method == 'POST':
        id = request.POST.get('userId', 0)
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        name = request.POST.get('name',None)
        email = request.POST.get('email',None)
        role = request.POST.get('role',None)
        start_date = request.POST.get('start_date',None)
        end_date = request.POST.get('end_date',None)
        metrics = request.POST.getlist('metrics',None)
        try:
            tempUser = User.objects.filter(id=id)
            if tempUser.exists():
                tempUser = tempUser.first()
                tempUser.first_name = name
                tempUser.email = email
                tempUser.save()
                userProfile = UserProfile.objects.get(user=tempUser)
                userProfile.role = role
                userProfile.start_date = start_date
                userProfile.end_date = end_date
                userProfile.metrics.clear()
                userProfile.metrics.set(metrics)
                userProfile.save()
                return redirect('addUser')
        except:
            pass
        userObj = User.objects.create_user(username=username, password=password, first_name=name, email=email)
        userProfile = UserProfile(user=userObj, role=role, start_date=start_date, end_date=end_date)
        userProfile.save()
        userProfile.metrics.set(metrics)
        return redirect('addUser')
    users = UserProfile.objects.all()
    userData = []
    for user in users:
        userData.append({
            'id': user.user.id,
            'name': user.user.first_name,
        })
    metricsList = Metrics.objects.all()
    metricsData = []
    for metric in metricsList:
        metricsData.append({
            'id': metric.id,
            'question': metric.question,
            'metricId': str(metric.sub_criterion.criterion.criterionId) + "." + str(metric.sub_criterion.SubCriterionId) + "." + str(metric.metricId),
        })
    context = {
        'role': userProfile.role,
        'name': userProfile.user.first_name,
        'users': userData,
        'metrics': metricsData,
    } 
    return render(request, "userManager.html", context)

def getUserDetails(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    if userProfile.role != 'admin':
        return redirect('index')
    userId = request.GET.get('userId', None)
    if userId is None:
        return JsonResponse({
            'error': 'User Id is required'
        })
    userObj = User.objects.get(id=userId)
    userNew = UserProfile.objects.get(user=userObj)
    metricsList = userNew.metrics.all()
    metricsData = []
    for metric in metricsList:
        metricsData.append({
            'id': metric.id,
            'question': metric.question,
            'metricId': str(metric.sub_criterion.criterion.criterionId) + "." + str(metric.sub_criterion.SubCriterionId) + "." + str(metric.metricId),
        })
    data = {
        'id': userNew.user.id,
        'role': userNew.role,
        'username': userObj.username,
        'name': userNew.user.first_name,
        'email': userObj.email,
        'start_date': userNew.start_date,
        'end_date': userNew.end_date,
        'metrics': metricsData,
    }
    return JsonResponse(data)

def deleteUser(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    if userProfile.role != 'admin':
        return redirect('index')
    userId = request.GET.get('userId', None)
    if userId is None:
        return JsonResponse({
            'error': 'User Id is required'
        })
    userObj = User.objects.get(id=userId)
    userObj.delete()
    return JsonResponse({
        'success': 'User deleted successfully'
    })

def formEditor(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    if userProfile.role != 'admin':
        return redirect('index')
    criterionList = Criterion.objects.all()
    subCriterionList = SubCriterion.objects.all()
    context = {
        'role': userProfile.role,
        'name': userProfile.user.first_name,
        'criterions': criterionList,
        'subCriterions': subCriterionList,
    }
    return render(request, "formEditor.html", context)

def criterionManager(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    if userProfile.role != 'admin':
        return redirect('index')
    if request.method == 'POST':
        name = request.POST.get('criterionName')
        criterionId = request.POST.get('criterionId',0)
        id = request.POST.get('id',0)
        try:
            criterion = Criterion.objects.filter(id=id)
            if criterion.exists():
                criterion = criterion.first()
                criterion.name = name
                criterion.save()
                return redirect('formEditor')
        except:
            pass
        criterion = Criterion()
        criterion.criterionId = criterionId
        criterion.name = name
        criterion.created_by = user
        criterion.save()
        return redirect('formEditor')
    if request.method == 'DELETE':
        criterionId = request.GET.get('criterionId', None)
        if criterionId is None:
            return JsonResponse({
                'error': 'Criterion Id is required'
            })
        criterion = Criterion.objects.get(criterionId=criterionId)
        criterion.delete()
        return JsonResponse({
            'success': 'Criterion deleted successfully'
        })
    if request.method == "GET":
        criterionId = request.GET.get('criterionId', None)
        if criterionId is not None:
            criterion = Criterion.objects.get(criterionId=criterionId)
            return JsonResponse({
                'id': criterion.criterionId,
                'name': criterion.name,
            })
        criterionList = Criterion.objects.all()
        criterionData = []
        for criterion in criterionList:
            criterionData.append({
                'id': criterion.criterionId,
                'name': criterion.name,
            })
        context = {
            'role': userProfile.role,
            'name': userProfile.user.first_name,
            'criterions': criterionData,
        }
        return JsonResponse(criterionData)

def subCriterionManager(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    if userProfile.role != 'admin':
        return redirect('index')
    if request.method == 'POST':
        name = request.POST.get('subCriterionName')
        criterionId = request.POST.get('criterionId',0)
        subCriterionId = request.POST.get('subCriterionId', 0)
        id = request.POST.get('id',0)
        criterion = Criterion.objects.get(id=criterionId)
        try:
            subCriterion = SubCriterion.objects.filter(id=id)
            if subCriterion.exists():
                subCriterion = subCriterion.first()
                subCriterion.name = name
                subCriterion.criterion = criterion
                subCriterion.save()
                return redirect('formEditor')
        except:
            pass
        subCriterion = SubCriterion()
        subCriterion.name = name
        subCriterion.SubCriterionId = subCriterionId
        subCriterion.criterion = criterion
        subCriterion.created_by = user
        subCriterion.save()
        return redirect('formEditor')
    if request.method == 'DELETE':
        subCriterionId = request.GET.get('subCriterionId', None)
        if subCriterionId is None:
            return JsonResponse({
                'error': 'SubCriterion Id is required'
            })
        subCriterion = SubCriterion.objects.get(SubCriterionId=subCriterionId)
        subCriterion.delete()
        return JsonResponse({
            'success': 'SubCriterion deleted successfully'
        })
    if request.method == "GET":
        subCriterionId = request.GET.get('subCriterionId', None)
        if subCriterionId is not None:
            subCriterion = SubCriterion.objects.get(SubCriterionId=subCriterionId)
            return JsonResponse({
                'id': subCriterion.SubCriterionId,
                'name': subCriterion.name,
                'criterionId': subCriterion.criterion.criterionId,
            })
        subCriterionList = SubCriterion.objects.all()
        subCriterionData = []
        for subCriterion in subCriterionList:
            subCriterionData.append({
                'id': subCriterion.SubCriterionId,
                'name': subCriterion.name,
                'criterionId': subCriterion.criterion.criterionId,
            })
        context = {
            'role': userProfile.role,
            'name': userProfile.user.first_name,
            'subCriterions': subCriterionData,
        }
        return JsonResponse(subCriterionData)

def metricManager(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    if request.method == "GET":
        metricId = request.GET.get('metricId', None)
        if metricId is not None:
            metric = Metrics.objects.get(metricId=metricId)
            return JsonResponse({
                'id': metric.metricId,
                'question': metric.question,
                'answer': metric.answer,
                'subCriterionId': metric.sub_criterion.SubCriterionId,
            })
        if userProfile.role != 'admin':
            metricList = userProfile.metrics.all()
        else:
            metricList = Metrics.objects.all()
        metricData = []
        for metric in metricList:
            metricData.append({
                'id': metric.metricId,
                'question': metric.question,
                'answer': metric.answer,
                'subCriterionId': metric.sub_criterion.SubCriterionId,
                'hint':metric.hint
            })
        context = {
            'role': userProfile.role,
            'name': userProfile.user.first_name,
            'metrics': metricData,
        }
        return JsonResponse(metricData)
    if userProfile.role != 'admin':
        return redirect('index')
    if request.method == 'POST':
        question = request.POST.get('metricQuestion')
        metricId = request.POST.get('metricId',0)
        id = request.POST.get('id',0)
        subCriterionId = request.POST.get('subCriterionId',0)
        maxLength = request.POST.get('maxLength',50000)
        hint = request.POST.get('hint')
        datatemplate = request.POST.get('template')

        subCriterion = SubCriterion.objects.get(id=subCriterionId)
        try:
            metric = Metrics.objects.filter(id=id)
            if metric.exists():
                metric = metric.first()
                metric.question = question
                metric.sub_criterion = subCriterion
                metric.max_length = maxLength
                if datatemplate is not None:
                    metric.dataTemplate = datatemplate
                

                metric.hint = hint
                metric.save()
                return redirect('formEditor')
        except:
            pass
        metric = Metrics()
        metric.question = question
        metric.metricId = metricId
        metric.sub_criterion = subCriterion
        metric.created_by = user
        metric.max_length = maxLength
        if datatemplate is not None:
            metric.dataTemplate = datatemplate
        metric.hint = hint
        metric.save()
        return redirect('formEditor')
    if request.method == 'DELETE':
        metricId = request.GET.get('metricId', None)
        if metricId is None:
            return JsonResponse({
                'error': 'Metric Id is required'
            })
        metric = Metrics.objects.get(metricId=metricId)
        metric.delete()
        return JsonResponse({
            'success': 'Metric deleted successfully'
        })

@csrf_exempt
def sendEmail(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    if userProfile.role != 'admin':
        return redirect('index')
    
    if request.method == "POST":
        
        userName = request.POST.get('userName')
        notAnswerd = request.POST.get('notAnswered')

        user = User.objects.get(first_name=userName)
        useremail = user.email

        # useremail = UserProfile.objects.get(user__first_name=userName).first()
        # print(userName,notAnswerd,useremail)

        subject = 'Testing Mail for NAD Data Entry Reminder'
        message = 'This is Test Mail for Testing SMTP Service'
        sender_email = 'jaivin_barot@daiict.ac.in'
        recipient_email = useremail
        context = {'name': user.first_name,'notAnswerd':notAnswerd ,'sender_name' : request.user.first_name }
        html_message = render_to_string('email_template.html',context)

        send_mail(subject, message, sender_email, [recipient_email], html_message=html_message,fail_silently=True)
        # send_mail(subject,message,sender_email,[recipient_email],fail_silently=False)
            # html_message=html_message,,

        return JsonResponse({
            'success': 'Email sent successfully'
        })

def Dashboard(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    user1 = request.user
    userProfile = UserProfile.objects.get(user=user1)
    users = UserProfile.objects.filter(role='editor')
    users_answered_not_answered = []
    for user in users:
        assigned_metrics = UserProfile.objects.filter(user=user.user).first().metrics.all()
        not_answered = []
        answerd = []
        for metric in assigned_metrics:
            if metric.answer == '':
                not_answered.append(metric)
            else:
                answerd.append(metric)

        users_answered_not_answered.append({
            'userName': user.user.first_name,
            'assigned':assigned_metrics.__len__(),
            'answered': len(answerd),
            'not_answered': len(not_answered),
        })
    content = {
        'name': userProfile.user.first_name,
        'role': userProfile.role,
        'users_answered_not_answered': users_answered_not_answered
    }
    return render(request,'dashboard.html',content)




def DataTemplateNone(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    if userProfile.role != 'admin':
        return redirect('index')
   #all the metrics form Criterin 1 will have data template none
    metrics = Metrics.objects.filter(sub_criterion__criterion__criterionId=1)
    for metric in metrics:
        metric.dataTemplate = None
        metric.save()
    return redirect('index')