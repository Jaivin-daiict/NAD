from django.db import models
from django.contrib.auth.models import User


class Criterion(models.Model):
    criterionId = models.IntegerField(default=0)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.criterionId) + " - " + self.name


class SubCriterion(models.Model):
    SubCriterionId = models.IntegerField(default=0)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.criterion.criterionId)+"."+str(self.SubCriterionId) + " - " + self.name


class Metrics(models.Model):
    metricId = models.IntegerField(default=0)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    max_length = models.IntegerField(default=50000)
    hint = models.TextField(blank=True, null=True)
    answered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answered_by', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by')
    sub_criterion = models.ForeignKey(SubCriterion, on_delete=models.CASCADE)
    dataTemplate = models.FileField(upload_to='templates/', blank=True, null=True)
    dataTemplateUploaded = models.FileField(upload_to='templates/', blank=True, null=True)


    def __str__(self):
        return str(self.metricId) + " - " + self.question


class Document(models.Model):
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    metrics = models.ForeignKey(Metrics, on_delete=models.CASCADE)
    documentFile = models.FileField(upload_to='documents/', blank=True, null=True)

    def __str__(self):
        return self.description


# Create your models here.
class UserProfile(models.Model):
    roles = (
        ('admin', 'admin'),
        ('editor', 'editor'),
        ('viewer', 'viewer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=roles, default='viewer')
    metrics = models.ManyToManyField(Metrics, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    def __str__(self):
        return self.user.username
