from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
import openai
import os
import re
import tiktoken


class Main(View):

    def get(self, request, *args, **kwargs):
        return render(request, "index.html")

    def post(self, request, *args, **kwargs):

        model = "gpt-3.5-turbo"

        API_KEY = os.getenv("OPENAI_KEY")
        if not API_KEY:
            return HttpResponse(status=500)

        script = request.POST["l_script"]
        num_questions = request.POST["q_amount"]
        type_questions = request.POST["q_type"]

        num_distractors = int(request.POST["q_distractors"]) or 2

        if type_questions == "MCQ":
            content = f"{num_questions} multiple-choice questions with "
            content += f"{num_distractors + 1} options and {num_distractors} "
            content += "distractors. Do not use distractors such as 'all of the "
            content += "above' or 'none of the above'. Indicate the correct answer at the bottom."
            content += "Ensure the questions are only based on the supplied content."
            user_content = f"Generate {content}. Generate the questions based on this script ```{script}```"
        elif type_questions == "variations":
            user_content = f"Create {num_distractors} new distractors for the following questions."
            user_content += f"Use the same format and indicate the correct answer: ```{script}```"
        elif type_questions == "coding knowledge":
            content = f"{num_questions} {type_questions} questions."
            content += "Ensure the questions are only based on the supplied content."
            user_content = f"Generate {content}. The questions may require the user to write some code in the "
            user_content += f"programming language used in the script. Generate the questions based on this script ```{script}```"
        elif type_questions == "maths":
            model = "gpt-4"
            content = f"{num_questions} multiple-choice questions with "
            content += f"{num_distractors + 1} options and {num_distractors} "
            content += "distractors. Do not use distractors such as 'all of the "
            content += "above' or 'none of the above'. Indicate the correct answer at the bottom."
            content += "Provide formulas in LaTeX format"
            user_content = f"Generate {content}. Generate the questions based on this script ```{script}```"
        else:
            content = f"{num_questions} {type_questions} questions."
            content += "Ensure the questions are only based on the supplied content."
            user_content = f"Generate {content}. Generate the questions based on this script ```{script}```"

        messages = [
            {"role": "system", "content": "Your role is to create assessment questions for coding-related questions.  Answers should be delivered with no preamble."},
            {"role": "user", "content": user_content}]

        enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

        if len(enc.encode(script)) > 4500:
            result = f"This script {len(enc.encode(code))} is too long for the beta peer reviewer"
        else:
            openai.api_key = API_KEY
            response = openai.ChatCompletion.create(
                model=model, messages=messages)

            final_content = {
                "content": "",
                "mcq": ""
            }

            if type_questions == "MCQ":
                system = "Perform the following two operations on the attached multiple-choice questions: "
                system += "First, replace any commas with &#44. "
                system += "Second, reformat the questions below as CSV in this format with headings: "
                system += "question,correct, optb,optc,optd where 'question' is the question, "
                system += "'correct' is the correct answer, 'optb', 'optc' and 'optd' are the distractors. "
                messages = [
                    {"role": "system", "content": system},
                    {"role": "user", "content": "The questions are: " + response["choices"][0]["message"]["content"]}]

                mcq = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", messages=messages)

                final_content["mcq"] = re.sub(
                    r"[a-zA-Z]\)\s", "", mcq["choices"][0]["message"]["content"])

            final_content["content"] = response["choices"][0]["message"]["content"].replace(
                "\n", "<br>")

        return JsonResponse(final_content, status=200)
