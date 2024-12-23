from . import views
from django.urls import path

urlpatterns = [
    path("", views.index, name="index"),
    path("signin/", views.signin, name="signin"),
    path("signout/", views.signout, name="signout"),
    path("add-user/", views.addUser, name="addUser"),
    path("get-user-details/", views.getUserDetails, name="getUserDetails"),
    path("delete-user/", views.deleteUser, name="deleteUser"),
    path("form-editor/", views.formEditor, name="formEditor"),
    path("manage-criterion/", views.criterionManager, name="criterionManager"),
    path("manage-sub-criterion/", views.subCriterionManager, name="subCriterionManager"),
    path("manage-metrics/", views.metricManager, name="metricManager"),
    path('send-email/', views.sendEmail, name='sendEmail'),
    path('dashboard/', views.Dashboard, name='Dashboard'),
    path('DataTemplateNone/', views.DataTemplateNone, name='DataTemplateNone'),
]
