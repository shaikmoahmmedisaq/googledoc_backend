from rest_framework import serializers
from .models import Question, Form, Choice, Response, Answer


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        exclude = ['created_at', 'updated_at']


class QuestionSerializer(serializers.ModelSerializer):

    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question', 'choices', 'required', 'question_type']


class FormSerializer(serializers.ModelSerializer):

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Form
        fields = ['id', 'code', 'title','background_color', 'questions', ]





# class AnswerInputSerializer(serializers.Serializer):
#     question_id = serializers.IntegerField()
#     selected_choice = serializers.IntegerField(required=False, allow_null=True)  # Allow null for single-answer MCQs
#     selected_choices = serializers.ListField(
#         child=serializers.IntegerField(), required=False  # For multi-answer MCQs
#     )
#     text_answer = serializers.CharField(required=False, allow_blank=True)
#
#     def validate(self, attrs):
#         question = Question.objects.get(id=attrs['question_id'])
#
#         if question.question_type == 'single':
#             if 'selected_choice' not in attrs or attrs['selected_choice'] is None:
#                 raise serializers.ValidationError("A single-choice MCQ must have a selected choice.")
#             if 'selected_choices' in attrs and attrs['selected_choices']:
#                 raise serializers.ValidationError("Single-choice MCQ cannot have multiple selected choices.")
#         elif question.question_type == 'multi':
#             if 'selected_choices' not in attrs or not attrs['selected_choices']:
#                 raise serializers.ValidationError("A multi-choice MCQ must have selected choices.")
#             if 'selected_choice' in attrs and attrs['selected_choice'] is not None:
#                 raise serializers.ValidationError("Multi-choice MCQ cannot have a single selected choice.")
#
#         return attrs

#
# class ResponseInputSerializer(serializers.Serializer):
#     submitter_email = serializers.EmailField(max_length=100)
#     answers = AnswerInputSerializer(many=True)
#
#     def create(self, validated_data):
#         # Extract form from context
#         form = self.context.get('form')
#
#         # Create the Response object
#         response = Response.objects.create(
#             form=form,
#             submitter_email=validated_data.get('submitter_email')
#         )
#
#         # Create associated answers
#         for answer_data in validated_data['answers']:
#             answer_serializer = AnswerInputSerializer(data=answer_data)
#             answer_serializer.is_valid(raise_exception=True)
#
#             # Extract validated data
#             question = Question.objects.get(id=answer_serializer.validated_data['question_id'])
#             answer = Answer.objects.create(
#                 response=response,
#                 question=question,
#                 text_answer=answer_serializer.validated_data.get('text_answer', '')
#             )
#
#             # Handle single choice
#             selected_choice_id = answer_serializer.validated_data.get('selected_choice')
#             if selected_choice_id is not None:
#                 try:
#                     selected_choice = Choice.objects.get(id=selected_choice_id)
#                     answer.selected_choice = selected_choice
#                     answer.save()
#                 except Choice.DoesNotExist:
#                     raise serializers.ValidationError({"selected_choice": f"Choice with id {selected_choice_id} does not exist."})
#
#             # Handle multiple choices
#             selected_choices_ids = answer_serializer.validated_data.get('selected_choices', [])
#             if selected_choices_ids:
#                 choices = Choice.objects.filter(id__in=selected_choices_ids)
#                 if not choices.exists():
#                     raise serializers.ValidationError({"selected_choices": "One or more selected choices do not exist."})
#                 answer.selected_choices.set(choices)
#
#         return response


class AnswerSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all())  # This should link the answer to a question
    selected_choice = serializers.PrimaryKeyRelatedField(queryset=Choice.objects.all(), required=False, allow_null=True)
    selected_choices = serializers.PrimaryKeyRelatedField(queryset=Choice.objects.all(), many=True, required=False,
                                                          allow_empty=True)
    text_answer = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Answer
        fields = ['question', 'selected_choice', 'selected_choices', 'text_answer']

    def validate(self, attrs):
        question = attrs.get('question')
        # Validate single-choice questions
        if question.question_type == 'single choice':
            if not attrs.get('selected_choice'):
                raise serializers.ValidationError("A single-choice question must have a selected choice.")
            if attrs.get('selected_choices'):
                raise serializers.ValidationError("Single-choice question cannot have multiple selected choices.")

        # Validate multi-choice questions
        elif question.question_type == 'multi choice':
            if not attrs.get('selected_choices'):
                raise serializers.ValidationError("A multi-choice question must have selected choices.")
            if attrs.get('selected_choice'):
                raise serializers.ValidationError("Multi-choice question cannot have a single selected choice.")

        return attrs


class ResponseInputSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Response
        fields = ['submitter_email', 'answers']

    def create(self, validated_data):
        form = self.context.get('form')  # Get the form from context

        answers_data = validated_data.pop('answers')
        response = Response.objects.create(form=form, **validated_data)

        for answer_data in answers_data:
            # Handle the selected_choices (many-to-many field) properly
            selected_choices = answer_data.pop('selected_choices', [])

            # Create the Answer object first
            answer = Answer.objects.create(response=response, **answer_data)

            # Now set the many-to-many relationship for selected_choices
            answer.selected_choices.set(selected_choices)

        return response

# Why pop inside the loop:
# The pop inside the loop is used to extract and handle the selected_choices (many-to-many relationship) separately for each answer. This ensures that the Answer object is created without the selected_choices initially, and the relationship is properly set afterward using set().
# It prevents accidental storing of unnecessary data in the Response object and allows the Answer object to be created correctly with the many-to-many relationship being properly handled.

