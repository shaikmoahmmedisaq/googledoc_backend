import uuid
from django.db import models
from .choices import QUESTION_CHOICES
from django.contrib.auth.models import User

# Create your models here.


class BaseModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # This metaclass we need to define to allow other classes to inherit this model
    class Meta:
        abstract = True


class Choice(BaseModel):
    choice = models.CharField(max_length=100)

    def __str__(self):
        return self.choice

class Question(BaseModel):
    question = models.CharField(max_length=200)
    question_type = models.CharField(max_length=200, choices=QUESTION_CHOICES)
    required = models.BooleanField(default=True)
    choices = models.ManyToManyField(Choice, related_name='question_choices', blank=True)

    def __str__(self):
        return self.question


class Form(BaseModel):
    code = models.UUIDField(default=uuid.uuid4,editable=False, unique=True)
    title = models.CharField(max_length=200)
    creator = models.ForeignKey(User, related_name='creator', on_delete=models.CASCADE)
    background_color = models.CharField(max_length=100, default='#3f363c')
    questions = models.ManyToManyField(Question, related_name='questions', blank=True)

    def __str__(self):
        return str(self.code)


class Response(BaseModel):
    form = models.ForeignKey(Form, related_name='responses', on_delete=models.CASCADE)
    submitter_email = models.EmailField(max_length=100)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.form.title} by {self.submitter_email or 'Anonymous'}"


class Answer(BaseModel):
    """
    Represents an answer to a specific question in a form response.
    """
    response = models.ForeignKey(Response, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, related_name='single_answers', on_delete=models.SET_NULL, blank=True,
                                        null=True)  # For single-answer MCQs
    selected_choices = models.ManyToManyField(Choice, related_name='multi_answers',
                                              blank=True)  # For multiple-choice answers
    text_answer = models.TextField(blank=True, null=True)  # For text-based answers

    def __str__(self):
        return f"Answer to {self.question.question}"


