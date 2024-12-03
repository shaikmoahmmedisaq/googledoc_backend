from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response as DRFResponse
from .serializers import QuestionSerializer, FormSerializer, ResponseInputSerializer
from .models import Question, Form, Response, Answer
from rest_framework import status

class QuestionView(APIView):
    def get(self, request):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return DRFResponse(serializer.data)

class FormView(APIView):
    def get(self, request, pk):
        try:
            queryset = Form.objects.get(code=pk)
            serializer = FormSerializer(queryset)
        except Exception as e:
            return DRFResponse({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        return DRFResponse(serializer.data)



class FormResponseView(APIView):
    def post(self, request, pk):
        # Step 1: Get the form object with all the attributes by using form_code from the URL
        form = get_object_or_404(Form, code=pk)  # Retrieve the form by its code (pk)

        # Step 2: Pass the form into the serializer context to associate it with the response
        # The context allows passing additional data (like the form) that the serializer needs
        serializer = ResponseInputSerializer(data=request.data, context={'form': form})

        # Step 3: Validate the request data
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return DRFResponse(e.detail, status=400)

        # Step 4: Use the serializer's save method to save the response and related answers
        serializer.save()

        # Step 5: Return success response
        return DRFResponse({"message": "Response submitted successfully"}, status=201)

