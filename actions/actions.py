# rasa run --enable-api --cors="*"
# rasa run actions

# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Dict, List, Text, Union
import random
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, Form, FollowupAction
from rasa_sdk import Action, FormValidationAction, forms

import json

import os
from openai import OpenAI
from dotenv import load_dotenv

# import re
from fpdf import FPDF

import ollama
from reportlab.pdfgen import canvas 
from reportlab.pdfbase.ttfonts import TTFont 
from reportlab.pdfbase import pdfmetrics 
from reportlab.lib import colors 
import mysql.connector


# import mysql.connector
# from mysql.connector import errorcode

load_dotenv()
OPENAI_KEY = "12345678765432" #os.getenv("OPENAI_API_KEY")
client = OpenAI(
  api_key=OPENAI_KEY
)

# config = {
#     'host': '127.0.0.1',  # or your MySQL server host
#     'user':'root', 
#     'password':"",
#     # Add 'user' and 'password' fields if your MySQL server requires them
# }
# cnx = mysql.connector.connect(**config)
# cursor = cnx.cursor()
# cursor.execute("USE amelio")

PROMPT_TEMPLATE = """
You are an expert in drafting HR policies. I am currently working on creating an {job_type}. The policy will include the following condition: {flexible_work_option}.
Based on this specific clause, please provide a list of detailed questions to consider:
Output should be a list of length 5: [Question 1, Question 2, Question 3, Question 4, Question 5]
"""

with open('actions/predefined_questions.json', 'r') as file:
    predefined_questions = json.load(file)

def get_policy_from_db(table_name, attribute_name, value):
    value = value.lower()
    query = f"SELECT * FROM {table_name} WHERE {attribute_name}='{value}'"
    # cursor.execute(query)
    # result = cursor.fetchmany()
    # Returns list of policy
    # return result



class ActionGreet(Action):

    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        messages = ["Hi there. 👋😃 It's such a pleasure to have you here. How may I help you?",
                    "Hello, 🤗 how can we assist you?"]
        
        buttons = [
            # {"payload": "/job_posting", "title": "Job Posting"},
            # {"payload": '/hr_policy', "title": "HR Policy"},
            {"payload": '/select_option{"option": "selected_hr_policy"}', "title": "HR Policy"}
        ]

        reply = random.choice(messages)
        dispatcher.utter_message(text=reply, buttons=buttons)

        return []



class ActionHrPolicy(Action):
    
        def name(self) -> Text:
            return "action_hr_policy"
    
        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
            # buttons = [
            #     {"payload": "/hr_policy{'content_type': 'hr_policy'}", "title": "HR Policy"},
            #     {"payload": "/job_posting", "title": "Job Posting"}
            # ]
            try:
                hr_policy_type = tracker.get_slot("hr_policy_type")
            except:
                hr_policy_type = None
    
            if hr_policy_type:
                message = f"You selected: {hr_policy_type} policy."
                # policies = get_policy_from_db('hr_policy', 'policy_name', hr_policy_type)
                # Fetch all of remote work policies
                # query = f"SELECT hr_policy_type.* \
                #             FROM hr_policy_type \
                #             JOIN hr_policy ON hr_policy_type.hr_policy_id = hr_policy.id \
                #             WHERE hr_policy.policy_name = '{hr_policy_type}'; \
                #         "
                # cursor.execute(query)
                # policies = cursor.fetchmany()
                policies = [
                    ('flexible', 'Flexible Work'),
                    ('remote', 'Remote Work'),
                    ('part_time', 'Part-time Work'),
                    ('unpaid_leave', 'Unpaid Leave'),
                    ('job_sharing', 'Job Sharing')
                ]
                buttons = []
                if policies:
                    message += "\nHere are some templates for you:"
                    for p_template in policies:
                        # Suggest as button
                        buttons.append({
                            "payload": '/policy_type{"policy_name": "'+p_template[0]+'"}',
                            "title": p_template[1].capitalize()
                        })
                buttons.append(
                    {"payload": '/policy_type{"policy_name": None}', "title": "Create your own"}
                )
                dispatcher.utter_message(text=message, buttons=buttons)
            else:
                message = "You have selected HR policy. \nWhat policy would you like to create?"
                dispatcher.utter_message(text=message,)
    
            return []

class ActionPolicyType(Action):
        
        def name(self) -> Text:
            return "action_policy_type"
    
        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            try:
                selected_policy = tracker.get_slot('policy_name')
            except:
                selected_policy = None
            # query = f"SELECT * FROM hr_policy_type WHERE {attribute_name}='{value}'"
            # cursor.execute(query)
            # result = cursor.fetchmany()
            # selected_policy = get_policy_from_db('hr_policy_type', 'policy_name', selected_policy)
            selected_policy = 'flexible'
            if selected_policy.lower() == 'flexible':
                options = predefined_questions[selected_policy]
                buttons = []
                for key, option_val in options.items():
                    # buttons.append(
                    #     {
                    #         "label" : option_val,
                    #         "value": "/select_flexible_work_option{'flexible_work_option': '"+key+"'}"
                    #     }
                    # )
                    # "/select_flexible_work_option{'flexible_work_option': 'a'}"
                # message={"payload":"dropDown","data":buttons}
                    buttons.append({
                        "payload": '/select_flexible_work_option{"flexible_work_option": "'+key+'"}',
                        "title": option_val
                    })
                dispatcher.utter_message(text="Please select your flexible work option:", buttons=buttons)
                # dispatcher.utter_message(text="Please select your flexible work option:", attachment=message)
                # dispatcher.utter_message(text="Please select your flexible work option:", json_message=message)
            else:
                dispatcher.utter_message(text="No policy type selected")
            return []


class ActionSelectFlexibleWorkOption(Action):

    def name(self) -> Text:
        return "action_select_flexible_work_option"
    
    def generate_questions(self, prompt):
    # generating question for selected work options
        questions = [] #prompt_engineering(prompt=prompt)

    # storing generated question in json file
        try:
            with open("questions.json", 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        start_index = max(data.keys()) + 1 if data else 1

        for index, question in enumerate(questions, start_index):
            data[index] = question

        with open("flexible_work_questions.json", 'w') as f:
            json.dump(data, f, indent=4)

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        flexible_work_option = tracker.get_slot('flexible_work_option')
        option = tracker.get_slot('option').split('_')
        option = ' '.join(option[1:])
        hr_policy_type = tracker.get_slot('hr_policy_type')
        job_type = f'{hr_policy_type} for {option} work'
        selected_policy = tracker.get_slot('policy_name')
        flexible_work_option = predefined_questions[selected_policy].get(flexible_work_option)
        # prompt = PROMPT_TEMPLATE.format(job_type=job_type, flexible_work_option=flexible_work_option)
        # questions = prompt_engineering(prompt=prompt)

        # for option in flexible_work_option:
        #     option = tracker.get_slot('option').split('_')
        #     option = ' '.join(option[1:])
        #     hr_policy_type = tracker.get_slot('hr_policy_type')
        #     job_type = f'{hr_policy_type} for {option} work'
        #     selected_policy = tracker.get_slot('policy_name')
        #     flexible_work_option = predefined_questions[selected_policy].get(flexible_work_option)
        #     prompt = PROMPT_TEMPLATE.format(job_type=job_type, flexible_work_option=flexible_work_option)
        #     self.generate_questions(prompt)

        questions = "question" #flexible_questions["question_list"]
        attachments = {
            "questions": questions,
            "payload": "question_list"
        }
        # dispatcher.utter_attachment(attachment=attachments)
        dispatcher.utter_message(text=f"You have selected: {flexible_work_option}")
        dispatcher.utter_message(text="Please answer the following questions:")
        return [FollowupAction("action_set_question")]
        # return [SlotSet('flexible_work_option', flexible_work_option)]


class ActionGetQuestions(Action):
    def name(self) -> Text:
        return "action_get_questions"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        questions = flexible_questions["question"]
        return [{"questions": questions}]


def prompt_engineering(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content

yes_no_prompt = """
    Is the following answer relevant to the question {current_question}: '{user_answer}'? Answer with 'yes' or 'no' OR 'true' or 'false', without any additional explanation. .
    """

# class ValidateQuestionForm(FormValidationAction):
#     def name(self):
#         return "validate_question_form"
    

#     def validate_response(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
#         current_question = tracker.get_slot("question0")
#         user_answer = tracker.latest_message.get('text')
#         index = int(tracker.get_slot("question_index"))


#         prompt = yes_no_prompt.format(current_question=current_question, user_answer=user_answer)
#         answer_relevance = "yes" #prompt_engineering(prompt=prompt).lower()
#         print(answer_relevance)
        
#         if answer_relevance == "yes" or "true":
#             # return [SlotSet("question_index", index + 1), SlotSet("response", user_answer)]
#             return {"user_response": user_answer, "response": None} #[FollowupAction("action_custom_fallback")]
#         elif answer_relevance == "no" or "false":
#             updated_index = index - 1
#             dispatcher.utter_message(text="Please enter a answer relevant to the question.")
#             return {"question_index": updated_index, "response": None}
#             # return [SlotSet("question_index", index - 1), SlotSet("response", None)]
    


class ValidateQuestionForm(FormValidationAction):
    def name(self):
        return "validate_question_form"
    
    def validate_response(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        current_question = tracker.get_slot("question0")
        user_answer = tracker.latest_message.get('text')
        index = int(tracker.get_slot("question_index"))
        response_list = tracker.get_slot("user_response")
        user_response = tracker.get_slot("response")

        print(response_list)
        
        if response_list:
            updated_response_list = response_list + [user_answer]
        else:
            updated_response_list = user_answer
        
        prompt = yes_no_prompt.format(current_question=current_question, user_answer=user_answer)
        answer_relevance = "yes" #prompt_engineering(prompt=prompt).lower()

        if answer_relevance is "yes":
            print(f"flexible - {updated_response_list}")
            return {"user_response": updated_response_list}
        
        if answer_relevance is "no":
            updated_index = index - 1
            print(f"updated index - {updated_index}")
            dispatcher.utter_message(text="Please enter answer relevant to the question.")
            return {"question_index": updated_index}
    
    def submit(self, dispatcher, tracker, domain) -> List[Dict]:
        return [FollowupAction("action_set_question")]
    
with open('actions/flexible_questions.json', 'r') as file:
    flexible_questions = json.load(file)
try:
    with open('actions/questions.json', 'r') as file:
        questions = json.load(file)
except Exception as e:
    pass

class ActionSetQuestion(Action):
    def name(self) -> str:
        return "action_set_question"
    

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        question_list = {
                            "0": "How will the mandatory core period be enforced, and what tools or systems will be used to track employee hours?",
                            "1": "What provisions will be made for employees in different time zones, and how will this impact the mandatory core period?",
                            # "2": "How will the policy accommodate employees with varying personal responsibilities, such as childcare or eldercare?",
                            # "3": "What are the expectations for employee availability during the mandatory core period, and how will this be communicated?",
                            # "4": "How will the policy handle requests for exceptions or adjustments to the core hours due to unforeseen circumstances?",
                            # "5": "What guidelines will be provided for team meetings, collaboration, and communication within the flexible hours framework?",
                            # "6": "How will the policy ensure that flexible hours do not negatively impact productivity, team cohesion, or project deadlines?",
                            # "7": "What measures will be taken to ensure that employees do not feel pressured to work outside their chosen hours or beyond the core period?",
                            # "8": "What are the legal implications of implementing flexible hours, and how does the policy comply with local labor laws and regulations?",
                            # "9": "How will performance be evaluated for employees working flexible hours, and what criteria will be used to ensure fairness?"
                        }
        # question_list = questions
        index = int(tracker.get_slot("question_index"))
        print(f"set question index - {index}")
        question_index = str(index)
        if index >= len(question_list):
            # return [FollowupAction("action_store_response")]
            return [FollowupAction("action_select_applied_context"),
                    SlotSet("question_index", 0),
                    SlotSet("flexible_work_option", None)]
        else:
            return [SlotSet("question0", question_list[question_index]),
                    SlotSet("response", None),
                    FollowupAction("action_form")]
    
class ActionActivateForm(Action):
    def name(self):
        return "action_form"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        index = int(tracker.get_slot("question_index"))      
        return [SlotSet("question_index", index + 1), Form("question_form")]#,FollowupAction("action_custom_fallback")]
        # return [FollowupAction("action_custom_fallback")]


##########################################################################################################
with open('actions/apply_flexible_work_policy_questions.json', 'r') as file:
    applied_questions = json.load(file)
import pprint
class ActionSelectAppliedContexts(Action):
    def name(self) -> Text:
        return "action_select_applied_context"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        tracker.get_slot("user_response")
        options = applied_questions["applied_context"]
        buttons = []
        for key, option_val in options.items():

            buttons.append({
                    "payload": '/select_applied_context_option{"applied_context_option": "'+key+'"}',
                    "title": option_val
                })
        dispatcher.utter_message(text="Select the work situations where flexible work policy you would like to apply:", buttons=buttons)

        return []

APPLIED_CONTEXT_PROMPT_TEMPLATE = """ 

"""
# You are an expert in drafting HR policies. I am currently working on creating an {job_type}. The policy will include the following condition: {flexible_work_option}.
# Based on this specific clause, please provide a list of detailed questions to consider:
# Output should be a list of length 5: [Question 1, Question 2, Question 3, Question 4, Question 5]


class ActionAppliedContext(Action):
    def name(self):
        return "action_applied_content"
    
    def generate_questions(self, prompt):
        questions = [] #prompt_engineering(prompt=prompt)

    # storing generated question in json file
        try:
            with open("applied_context_questions.json", 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        start_index = max(data.keys()) + 1 if data else 1

        for index, question in enumerate(questions, start_index):
            data[index] = question

        with open("applied_context_questions.json", 'w') as f:
            json.dump(data, f, indent=4)

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        applied_context_option = tracker.get_slot('applied_context_option')
        applied_context = applied_questions["applied_context"].get(applied_context_option)

        # prompt = APPLIED_CONTEXT_PROMPT_TEMPLATE.format(applied_context_option=applied_context_option)
        # questions = prompt_engineering(prompt=prompt)

        # for option in flexible_work_option:
        #     prompt = APPLIED_CONTEXT_PROMPT_TEMPLATE.format(job_type=job_type, flexible_work_option=flexible_work_option)
        #     self.generate_questions(prompt)

        questions = "question" #flexible_questions["question_list"]
        attachments = {
            "questions": questions,
            "payload": "question_list"
        }
        # dispatcher.utter_attachment(attachment=attachments)
        dispatcher.utter_message(text=f"You have selected: {applied_context}")
        dispatcher.utter_message(text="Please answer the following questions:")
        return [FollowupAction("action_set_applied_context_question")]
    
class ActionAppliedContextSetQuestion(Action):
    def name(self) -> str:
        return "action_set_applied_context_question"
    

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        question_list = {
                            "0": "What are the key goals or objectives you hope to achieve during the six-month pilot period?",
                            "1": "What criteria will be used to evaluate the success or failure of the pilot project?",
                            "2": "What potential challenges or concerns do you anticipate facing during the pilot, and how do you plan to address them?",
                        }
        # question_list = questions
        index = int(tracker.get_slot("question_index"))
        print(f"set question index - {index}")
        question_index = str(index)
        # print(tracker.get_slot("applied_context_response"))
        if index >= len(question_list):
            # return [FollowupAction("action_store_response")]
            return [FollowupAction("action_eligibility_criteria"),
                    SlotSet("question_index", 0),
                    SlotSet("applied_context_option"), None]
        else:
            return [SlotSet("question0", question_list[question_index]),
                    SlotSet("response_applied_context", None),
                    FollowupAction("action_applied_context_form")]
  
class ActionActivateAppliedContextForm(Action):
    def name(self):
        return "action_applied_context_form"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        index = int(tracker.get_slot("question_index"))      
        return [SlotSet("question_index", index + 1), Form("applied_context_form")]
    
class ValidateQuestionForm(FormValidationAction):
    def name(self):
        return "validate_applied_context_form"
    
    def validate_response_applied_context(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        current_question = tracker.get_slot("question0")
        user_answer = tracker.latest_message.get('text')
        index = int(tracker.get_slot("question_index"))
        response_list = tracker.get_slot("applied_context_response")

        if response_list:
            updated_response_list = response_list + [user_answer]
        else:
            updated_response_list = user_answer
        
        prompt = yes_no_prompt.format(current_question=current_question, user_answer=user_answer)
        answer_relevance = "yes" #prompt_engineering(prompt=prompt).lower()

        if answer_relevance is "yes":
            print(f"applied - {updated_response_list}")
            return {"applied_context_response": updated_response_list}
        
        if answer_relevance is "no":
            updated_index = index - 1
            print(f"updated index - {updated_index}")
            dispatcher.utter_message(text="Please enter answer relevant to the question.")
            return {"question_index": updated_index}
    
    def submit(self, dispatcher, tracker, domain) -> List[Dict]:
        return [FollowupAction("action_set_applied_context_question")]
    
####################################################################################################################
with open('actions/eligibility_criteria.json', 'r') as file:
    eligibility_criteria_questions = json.load(file)
    
class ActionSelectEligibilityCriteria(Action):
    def name(self) -> Text:
        return "action_select_eligibility_criteria"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        options = eligibility_criteria_questions["eligibility_criteria"]
        buttons = []
        for key, option_val in options.items():
            buttons.append({
                    "payload": '/select_eligibility_criteria_option{"eligibility_criteria_option": "'+key+'"}',
                    "title": option_val
                })
        dispatcher.utter_message(text="Select the eligibility criteria would you like to include in your flexible work policy:", buttons=buttons)

        return []
    
ELIGIBILITY_CRITERIA_PROMPT_TEMPLATE = """ 

"""
# You are an expert in drafting HR policies. I am currently working on creating an {job_type}. The policy will include the following condition: {flexible_work_option}.
# Based on this specific clause, please provide a list of detailed questions to consider:
# Output should be a list of length 5: [Question 1, Question 2, Question 3, Question 4, Question 5]


class ActionEligibilityCriteria(Action):
    def name(self):
        return "action_eligibility_criteria"
    
    def generate_questions(self, prompt):
        questions = [] #prompt_engineering(prompt=prompt)

    # storing generated question in json file
        try:
            with open("eligibility_criteria_questions.json", 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        start_index = max(data.keys()) + 1 if data else 1

        for index, question in enumerate(questions, start_index):
            data[index] = question

        with open("eligibility_criteria_questions.json", 'w') as f:
            json.dump(data, f, indent=4)

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        eligibility_criteria_option = tracker.get_slot('eligibility_criteria_option')
        eligibility_criteria_option = eligibility_criteria_questions["eligibility_criteria"].get(eligibility_criteria_option)

        # prompt = ELIGIBILITY_CRITERIA_PROMPT_TEMPLATE.format(eligibility_criteria_option=eligibility_criteria_option)
        # questions = prompt_engineering(prompt=prompt)

        # for option in eligibility_criteria_option:
        #     prompt = ELIGIBILITY_CRITERIA_PROMPT_TEMPLATE.format(eligibility_criteria_option=eligibility_criteria_option)
        #     self.generate_questions(prompt)

        questions = "question" #flexible_questions["question_list"]
        attachments = {
            "questions": questions,
            "payload": "question_list"
        }
        # dispatcher.utter_attachment(attachment=attachments)
        dispatcher.utter_message(text=f"You have selected: {eligibility_criteria_option}")
        dispatcher.utter_message(text="Please answer the following questions:")
        return [FollowupAction("action_set_eligibility_criteria_question")]
    
class ActionEligibilityCriteriaQuestion(Action):
    def name(self) -> str:
        return "action_set_eligibility_criteria_question"
    

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        question_list = {
                            "0": "What specific job roles or functions do you consider as requiring constant physical presence and thus would not be eligible for flexible work arrangements?",
                            "1": "Are there any conditions under which roles typically requiring constant physical presence might still be considered for flexible work options?",
                            "2": "How will you determine and communicate which full-time and part-time positions are eligible for flexible work arrangements?"
                        }
        # question_list = questions
        index = int(tracker.get_slot("question_index"))
        print(f"set question index - {index}")
        question_index = str(index)
        print(tracker.get_slot("eligibility_criteria_response"))
        if index >= len(question_list):
            return [FollowupAction("action_store_response"),
                    SlotSet("eligibility_criteria_option", None)]
            # return [FollowupAction(""),
            #         SlotSet("question_index", 0)]
        else:
            return [SlotSet("question0", question_list[question_index]),
                    SlotSet("response", None),
                    FollowupAction("action_eligibility_criteria_form")]
  
class ActionActivateEligibilityCriteriaForm(Action):
    def name(self):
        return "action_eligibility_criteria_form"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        index = int(tracker.get_slot("question_index"))      
        return [SlotSet("question_index", index + 1), Form("eligibility_criteria_form")]
    
class ValidateQuestionForm(FormValidationAction):
    def name(self):
        return "validate_eligibility_criteria_form"
    
    def validate_response(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        current_question = tracker.get_slot("question0")
        user_answer = tracker.latest_message.get('text')
        index = int(tracker.get_slot("question_index"))
        response_list = tracker.get_slot("eligibility_criteria_response")
        print(tracker.get_slot("response"))

        if response_list:
            updated_response_list = response_list + [user_answer]
        else:
            updated_response_list = user_answer
        
        prompt = yes_no_prompt.format(current_question=current_question, user_answer=user_answer)
        answer_relevance = "yes" #prompt_engineering(prompt=prompt).lower()

        if answer_relevance is "yes":
            print(updated_response_list)
            return {"eligibility_criteria_response": updated_response_list}
        
        if answer_relevance is "no":
            updated_index = index - 1
            print(f"updated index - {updated_index}")
            dispatcher.utter_message(text="Please enter answer relevant to the question.")
            return {"question_index": updated_index}
    
    def submit(self, dispatcher, tracker, domain) -> List[Dict]:
        return [FollowupAction("action_set_eligibility_criteria_question")]

class ActionStoreResponse(Action):
    def name(self):
        return "action_store_response"
    
    def save_pdf(self, response):
        response = response
        question = flexible_questions["question_list"]
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        # flexible work policy
        pdf.cell(200, 10, txt="Policy Questions and Responses", ln=True, align='C')
        for num in range(10):
            pdf.multi_cell(200, 10, txt=question[str(num)], align='L')
            pdf.multi_cell(200, 10, txt= "Ans:" + response[num], align='L')
        
        # contexts likely to apply flexible work policy
        pdf.cell(200, 10, txt="contexts likely to apply flexible work policy", ln=True, align='C')
        for num in range(10):
            pdf.multi_cell(200, 10, txt=question[str(num)], align='L')
            pdf.multi_cell(200, 10, txt= "Ans:" + response[num], align='L')

        # eligibility criteria
        pdf.cell(200, 10, txt="eligibility criteria", ln=True, align='C')
        for num in range(10):
            pdf.multi_cell(200, 10, txt=question[str(num)], align='L')
            pdf.multi_cell(200, 10, txt= "Ans:" + response[num], align='L')
        pdf.output("Policy_Questions_and_Responses.pdf")
         
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        dispatcher.utter_message(text="Your responses are recorded")
        response = tracker.get_slot("response")
        self.save_pdf(response)

        dispatcher.utter_message(text="Saved in 'Policy_Questions_and_Responses.pdf' file!!!")
        return [] #[FollowupAction("action_select_applied_context")]
    
class actionCustomFallback(Action):
    def name(self):
        return "action_custom_fallback"       
        
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any])  -> List[Dict[Text, Any]]:
        index = int(tracker.get_slot("question_index"))
        updated_index = index - 1
        dispatcher.utter_message(text="I failed to understand you. Will you please rephrase the answer !!")
        flexible_work_option = tracker.get_slot("flexible_work_option")
        applied_context_option = tracker.get_slot("applied_context_option")
        eligibility_criteria_option = tracker.get_slot("eligibility_criteria_option")
        if (flexible_work_option == "a" or "b" or "c" or "d" or "e" or "f" or "g"):
            return [SlotSet("question_index", updated_index),
                    SlotSet("response", None),
                    FollowupAction("action_set_question")]
        elif (applied_context_option == "a" or "b" or "c" or "d"):
            return [SlotSet("question_index", updated_index),
                    SlotSet("response", None),
                    FollowupAction("action_set_applied_context_question")]
        elif (eligibility_criteria_option == "a" or "b" or "c" or "d" or "e" or "f"):
            return [SlotSet("question_index", updated_index),
                    SlotSet("response", None),
                    FollowupAction("action_set_eligibility_criteria_question")]


