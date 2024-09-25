# from docx import Document
# from docx.shared import Pt, Inches, RGBColor
# from docx.enum.text import WD_ALIGN_PARAGRAPH
# from docx.oxml import OxmlElement
# from docx.oxml.ns import qn

# def createDocument(company_name, brand_color, flexible_response, applied_response, eligibility_response, missing_response):
#         flexible_question = ["test question1", "test question2", "test question3"]
#         applied_question = ["test question1", "test question2", "test question3"]
#         eligibility_question = ["test question1", "test question2", "test question3"]
#         missing_question = ["test question1", "test question2", "test question3"]

#         doc = Document()

#         table = doc.add_table(rows=1, cols=1)
#         table.autofit = False
#         table.columns[0].width = Inches(10)
#         cell = table.cell(0, 0)

#         # Fill the cell with color
#         # Use RGBColor for color specification
#         cell._element.get_or_add_tcPr().append(
#             OxmlElement('w:shd', {
#                 qn('w:fill'): brand_color
#             })
#         )

        

#         # table = doc.add_table(rows=1, cols=2)

#         # cell_logo = table.cell(0, 0)
#         # paragraph_logo = cell_logo.add_paragraph()
#         # run_logo = paragraph_logo.add_run()
#         # run_logo.add_picture('pexels-helloaesthe-28056131.jpg', width=Inches(0.5), height=Inches(0.5))

#         # cell_text = table.cell(0, 1)
#         # paragraph_text = cell_text.add_paragraph()
#         # run_text = paragraph_text.add_run(company_name)
#         # run_text.font.name = 'Times New Roman'
#         # run_text.font.size = Pt(14)
#         # run_text.bold = True
#         doc.add_paragraph("\n")
#         doc.add_picture('pexels-helloaesthe-28056131.jpg', width=Inches(0.5), height=Inches(0.5))
#         doc.add_paragraph(company_name)

#         # Add a title
#         title = doc.add_heading('HR Policy', level=1)
#         title.alignment = WD_ALIGN_PARAGRAPH.CENTER
#         run = title.runs[0]
#         run.font.color.rgb = RGBColor(0,0,0)
        
#         policy = doc.add_heading('Policy Question Answers', level=2)
#         policy.add_run("\n")
#         run = policy.runs[0]
#         run.font.color.rgb = RGBColor(0,0,0)
#         run.font.name = 'Times New Roman' 
#         run.font.size = Pt(14)
#         policy.add_run("\n")

#         flexiblePolicy = doc.add_paragraph()
#         run = flexiblePolicy.add_run("Flexible work policy")
#         run.bold = True
#         flexiblePolicy.add_run("\n")
#         for num in range(len(flexible_question)):
#             run = flexiblePolicy.add_run(flexible_question[num])
#             flexiblePolicy.add_run("\n")
#             run = flexiblePolicy.add_run(f"Ans: {flexible_response[num]}")
#             flexiblePolicy.add_run("\n")

#         for run in flexiblePolicy.runs:
#             run.font.name = 'Times New Roman'
#             run.font.size = Pt(12)

#         appliedContext = doc.add_paragraph()
#         run = appliedContext.add_run("Applied Context")
#         run.bold = True
#         appliedContext.add_run("\n")
#         for num in range(len(applied_question)):
#             run = appliedContext.add_run(applied_question[num])
#             appliedContext.add_run("\n")
#             run = appliedContext.add_run(f"Ans: {applied_response[num]}")
#             appliedContext.add_run("\n")

#         for run in appliedContext.runs:
#             run.font.name = 'Times New Roman'
#             run.font.size = Pt(12)

#         eligibilityCriteria = doc.add_paragraph()
#         run = eligibilityCriteria.add_run("Eligibility Criteria")
#         run.bold = True
#         eligibilityCriteria.add_run("\n")
#         for num in range(len(eligibility_question)):
#             run = eligibilityCriteria.add_run(eligibility_question[num])
#             eligibilityCriteria.add_run("\n")
#             run = eligibilityCriteria.add_run(f"Ans: {eligibility_response[num]}")
#             eligibilityCriteria.add_run("\n")

#         for run in eligibilityCriteria.runs:
#             run.font.name = 'Times New Roman'
#             run.font.size = Pt(12)

#         missingElement = doc.add_paragraph()
#         run = missingElement.add_run("Missing Element")
#         run.bold = True
#         missingElement.add_run("\n")
#         for num in range(len(missing_question)):
#             run = missingElement.add_run(missing_question[num])
#             missingElement.add_run("\n")
#             run = missingElement.add_run(f"Ans: {missing_response[num]}")
#             missingElement.add_run("\n")

#         for run in missingElement.runs:
#             run.font.name = 'Times New Roman'
#             run.font.size = Pt(12)

#         # Save the document
#         doc.save(f'{company_name}_HR_document.docx')
#         return "Document Created..."

# company_name = "test Company"
# brand_color = "#FF0000"
# flexible_response = ["test response1", "test response2", "test response3"]
# applied_response = ["test response1", "test response2", "test response3"]
# eligibility_response = ["test response1", "test response2", "test response3"]
# missing_response = ["test response1", "test response2", "test response3"]
# document = createDocument(company_name, brand_color, flexible_response, applied_response, eligibility_response, missing_response)
# print(document)
import cohere
import os
from dotenv import load_dotenv
import PyPDF2

load_dotenv()

COHERE_KEY = os.getenv("COHERE_API_KEY")

co = cohere.Client(api_key=COHERE_KEY)


def prompt_engineering(prompt):
    response = co.chat(
        message=prompt,
        model="command-r-plus-08-2024",
        temperature=0.3
    )
    return response.text

ai_observation_prompt_template = """
This is a remote work HR policy, are we missing something in this HR policy?
Identify the missing elements in the following remote work HR policy:

{policy}

If there are any missing element in the provided policy, Return the missing elements separated by commas.
"""

missing_element_prompt = """
"Generate questions that address the following missing elements in a Remote Work HR policy: {missing_elements}
Avoid compound and tail questions under any circumstances. 
Do not provide any additional information beyond the questions"

Separator: |
"""


"""
Given the following list missing elements in the HR policy: 

{missing_elements}

Generate at two separate questions for each element, ensuring the questions are separated by a pipe character (|) only. 
Avoid compound or tail questions under any circumstances. 
Do not provide any additional information beyond the questions and do not add missing element in your response.
"""

def extract_text_from_pdf(pdf_file_path):
        try:
            with open(pdf_file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ''
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None

missing_elements = []
questions = []

def generate(pdf_file_path):
        extracted_text = extract_text_from_pdf(pdf_file_path)
        print("extracted!!")
        prompt = ai_observation_prompt_template.format(policy = extracted_text)
        missing_element = prompt_engineering(prompt=prompt)
        ele = missing_element.replace(", and", ",")
        elements_list = [element.strip() for element in ele.split(',') if element.strip()]
        missing_elements.append(elements_list)
        print("Generated missing ele!!")
        prompt = missing_element_prompt.format(missing_elements = missing_elements[0])
        question = prompt_engineering(prompt=prompt).replace("- ", "")
        question = question.replace("\n", "")

        question_list = [que.strip() for que in question.split('|')]
        questions.append(question_list)
        print("Generated questions!!")



pdf_file_path = "Policy_Questions_and_Responses.pdf"
generate(pdf_file_path)
print(missing_elements[0])
for question in questions[0]: 
     print(question)
