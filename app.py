import streamlit as st
from datetime import time as t
import time

from operator import itemgetter  
import os
import json
import getpass
import openai
import re
  
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings  
import pinecone


from results import results_agent
from filter import filter_agent
from reranker import reranker
from utils import build_filter, clean_pinecone
from keywords import keyword_agent

OPENAI_API = st.secrets["OPENAI_API"]
PINECONE_API = st.secrets["PINECONE_API"]
openai.api_key = OPENAI_API


pinecone.init(
    api_key= PINECONE_API,
    environment="gcp-starter" 
)
index_name = "use-class-db"

embeddings = OpenAIEmbeddings(openai_api_key = OPENAI_API)

index = pinecone.Index(index_name)

k = 35

st.title("USC GPT - Find the perfect class")

class_time = st.slider(
    "Filter Class Times:",
    value=(t(8, 30), t(18, 45))
)

units = st.slider(
    "Number of units",
    1, 4, 4
)

days = st.multiselect("What days are you free?",
               options = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
               default = None,
               placeholder = "Any day"
        )

assistant = st.chat_message("assistant")
initial_message = "Hello, I am your GPT-powered USC Class Helper! \n How can I assist you today?"



def get_rag_results(prompt):
    '''
1. Remove filters from the prompt to optimize success of the RAG-based step.
2. Query the Pinecone DB and return the top 25 results based on cosine similarity
3. Rerank the results from vector DB using a BERT-based cross encoder
    '''
    query = filter_agent(prompt, OPENAI_API)
    print("Here is the response from the filter_agent:", query)

    query += keyword_agent(query)
    print("Here is the new query with keywords added:", query)

  ##Get metadata filters  
    days_filter = list()
    start = float(class_time[0].hour) + float(class_time[0].minute) / 100.0
    end = float(class_time[1].hour) + float(class_time[1].minute) / 100.0
    query_filter = {
        "start": {"$gte": start},
        "end": {"$lte": end}
    }

    if units != "any":
        query_filter["units"] = str(int(units)) + ".0 units"

    if len(days) > 0:
        for i in range(len(days)):
            days_filter.append(days[i])
            for j in range(i+1, len(days)):
                two_day = days[i] + ", " +  days[j]
                days_filter.append(two_day)
        query_filter["days"] = {"$in": days_filter}

  ## Query the pinecone database
    response = index.query(
        vector = embeddings.embed_query(query),
        top_k = k,
        filter = query_filter,
        include_metadata = True
    )

    response, additional_metadata = clean_pinecone(response)
    if len(response) < 1:
        response = "No classes were found that matched your criteria"
        additional_metadata = "None"
    else:
        response = reranker(query, response) # BERT cross encoder for ranking 

    return response, additional_metadata

    

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": initial_message})
    st.session_state.rag_responses = []
    
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    

if prompt := st.chat_input("What kind of class are you looking for?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
            st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        messages = [{"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[-6:]]
        message_history = " ".join([message["content"] for message in messages])
        print("Prompt is", prompt)
        
        rag_response, additional_metadata = get_rag_results(prompt)
        rag_response = " ".join([message for message in rag_response])
        st.session_state.rag_responses.append(rag_response)
        print("Here is the session state responses", st.session_state.rag_responses)
        all_rag_responses = " ".join([response for response in st.session_state.rag_responses])
        result_query = 'Original Query:' + prompt
        # '\n Additional Class Times:' + str(additional_metadata)
        assistant_response = results_agent(result_query, "Class Options from RAG:" + all_rag_responses + "\nMessage_history" + message_history)
            # assistant_response = openai.ChatCompletion.create(
            #     model = "gpt-4",
            #     messages = [
            #         {"role": m["role"], "content": m["content"]}
            #         for m in st.session_state.messages
            #     ]
            # )["choices"][0]["message"]["content"]

        ## Display response regardless of route
        for chunk in re.split(r'(\s+)', assistant_response):
            full_response += chunk + " "
            time.sleep(0.02)
            message_placeholder.markdown(full_response + "▌")
        st.session_state.messages.append({"role": "assistant", "content": full_response})

