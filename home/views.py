from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
import openai
import os
import tiktoken


class Main(View):

    def get(self, request, *args, **kwargs):
        return render(request, "index.html")

    def post(self, request, *args, **kwargs):

        API_KEY = os.getenv("OPENAI_KEY")
        if not API_KEY:
            return HttpResponse(status=500)

        script = request.POST["l_script"]
        num_questions = request.POST["q_amount"]
        type_questions = request.POST["q_type"]
        num_distractors = int(request.POST["q_distractors"])
        if type_questions == "MCQ":
            content = f"{num_questions} multiple-choice questions with "
            content += f"{num_distractors + 1} options and {num_distractors} "
            content += "distractors. Do not use distractors such as 'all of the "
            content += "above' or 'none of the above'."
            user_content = f"Generate {content}. Generate the questions based on this script ```{script}```"
        elif type_questions == "variations":
            user_content = f"{num_questions} variations of the following questions ```{script}```"
        else:
            content = f"{num_questions} {type_questions} questions."
            user_content = f"Generate {content}. Generate the questions based on this script ```{script}```"

        messages = [
            {"role": "system", "content": "Your role is to create assessment questions for coding-related questions. Answers should be delivered with no preamble."},
            {"role": "user", "content": user_content}]

        enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

        if len(enc.encode(script)) > 4500:
            result = f"This script {len(enc.encode(code))} is too long for the beta peer reviewer"
        else:
            openai.api_key = API_KEY
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages)

            result = response["choices"][0]["message"]["content"].replace(
                "\n", "<br>")

        return HttpResponse(result, status=200)
