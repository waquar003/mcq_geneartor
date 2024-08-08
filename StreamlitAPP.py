import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file, get_table_data
import streamlit as st
from langchain.callbacks import get_openai_callback
from src.mcqgenerator.mcqgenerator import generate_evaluation_chain
from src.mcqgenerator.logger import logging

# loading json file
with open('Response.json', 'r') as file:
  RESPONSE_JSON = json.load(file)

#creating a titlle for the app
st.title("MCQs creator Application with Langchain and Gemini")


with st.form("user input"):
  uploaded_file=st.file_uploader("upload pdf or text")

  mcq_count=st.number_input("no of mcqs's", min_value=3, max_value=50)

  subject=st.text_input("Insert Subject", max_chars=20)

  tone=st.text_input("Complexity level of Questions", max_chars=20, placeholder="Simple")

  button=st.form_submit_button("Create MCQs")

  if button and uploaded_file is not None and mcq_count and subject and tone:
    with st.spinner("loading..."):
      try:
        text=read_file(uploaded_file)
        #Count tokens and the cost of api call
        
        response=generate_evaluation_chain(
          {
            "text": text,
            "number": mcq_count,
            "subject": subject,
            "tone": tone,
            "response_json": json.dumps(RESPONSE_JSON)
          }
        )
      except Exception as e:
        traceback.print_exception(type(e),e,e.__traceback__)
        st.error("error")

      else:
        #call of openai api tokens lien tokens cost etc..
        if isinstance(response, dict):
          #Extract the quiz data from the response
          # print(response)
          quiz=response.get("quiz")
          # quiz=json.dumps(quiz)
          if quiz is not None:
            table_data=get_table_data(quiz)
            if table_data is not None:
              print(table_data)
              df=pd.DataFrame(table_data)
              df.index=df.index+1
              st.table(df)
              #Display the review in a text box as well
              st.text_area(label="Review", value=response['review'])
            else:
              st.error("Error in table data")
        else:
          st.write(response)