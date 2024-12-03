from django.contrib import admin
from .models import Question, Choice, Form, Response, Answer

# Register your models here.

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice', 'id',)


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('code','id', 'title','background_color')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question','id','question_type', 'required')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ( 'question_id',  'question' , 'text_answer', 'selected_choice')

# admin.site.register(Response)
@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('form','id', 'submitter_email', 'submitted_at')