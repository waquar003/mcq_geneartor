import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file,get_table_data
from src.mcqgenerator.logger import logging

#imporing necessary packages packages from langchain
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

# Load environment variables from the .env file
load_dotenv()

# Access the environment variables just like you would with os.environ
api_key=os.getenv('GOOGLE_API_KEY')

llm = GoogleGenerativeAI(model="models/gemini-pro", google_api_key=api_key)


template="""
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz  of {number} multiple choice questions for {subject} students in {tone} tone. 
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like  RESPONSE_JSON below  and use it as a guide. \
Ensure to make {number} MCQs

{response_json}

"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=template)


quiz_chain=LLMChain(llm=llm,prompt=quiz_generation_prompt,output_key="quiz",verbose=True)

# from langchain_core import RunnableSequence

# quiz_chain = RunnableSequence(
#     steps=[
#         quiz_generation_prompt,
#         llm
#     ],
#     output_key="quiz",
#     verbose=True
# )


# from langchain_core import Prompt

# # Define your prompt and llm
# prompt = Prompt(quiz_generation_prompt)
# # llm = LLM(...)

# # Chain them together
# quiz_chain = prompt | llm


template2="""
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity analysis. 
if the quiz is not at per with the cognitive and analytical abilities of the students,\
update the quiz questions which needs to be changed and change the tone such that it perfectly fits the student abilities
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""


quiz_evaluation_prompt=PromptTemplate(input_variables=["subject", "quiz"], template=template2)

review_chain=LLMChain(llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True)

# from langchain_core import RunnableSequence

# review_chain = RunnableSequence(
#     steps=[
#         quiz_evaluation_prompt,
#         llm
#     ],
#     output_key="review",
#     verbose=True
# )


generate_evaluation_chain=SequentialChain(
  chains=[quiz_chain, review_chain],
  input_variables=["text", "number", "subject", "tone", "response_json"],
  output_variables=["quiz", "review"], verbose=True
  )