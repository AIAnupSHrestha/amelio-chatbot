import os
from openai import OpenAI
import cohere
from dotenv import load_dotenv
import pprint
load_dotenv()

COHERE_KEY = os.getenv("COHERE_API_KEY")

co = cohere.Client(api_key=COHERE_KEY)

def prompt_engineering(prompt):
    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo-0125",
    #     messages=[
    #         {"role": "user", "content": prompt},
    #     ],
    # )
    # return response.choices[0].message.content
    response = co.chat(
        message=PROMPT_TEMPLATE,
        model="command-r-plus-08-2024",
        temperature=0.3
    )
    return response.text
# yes_no_prompt = """
#     Is the following answer relevant to the question {current_question}: '{user_answer}'? Answer with 'yes' or 'no' OR 'true' or 'false', without any additional explanation..
#     """

PROMPT_TEMPLATE = """
You are an expert in drafting HR policies. I am currently working on creating a flexible work policy. 
The policy will include the following condition: flexible hours, where employees can choose their start and end times, with a mandatory core period (e.g., from 10 AM to 3 PM). 
Based on this specific clause, please provide 5 detailed questions to consider, separated by | only.
"""

# def prompt_engineering(prompt):
#     response = client.chat.completions.create(
#         model="GPT-Model",
#         messages=[
#             {"role": "user", "content": prompt},
#         ],
#     )
#     return response.choices[0].message.content

# current_question = "How will the mandatory core period be enforced, and what tools or systems will be used to track employee hours"
# user_answer = "The mandatory core period will be enforced through automated time-tracking software integrated with attendance systems to monitor and record employee hours."

# prompt = yes_no_prompt.format(current_question=current_question, user_answer=user_answer)

# print(prompt)
# list = []
answer_relevance = prompt_engineering(prompt=PROMPT_TEMPLATE).replace("\n", "")
print(answer_relevance)
print("")
print("1##################################################################################")
print("")
# answer_relevance = questions[1:-1]
# print(answer_relevance[0], answer_relevance[-1])

list = [question.strip() for question in answer_relevance.split('|')]
# print(answer_relevance)
# print("")
# print("2##################################################################################")
# print("")
# list.append(answer_relevance)
for q in list:
    print(q)

