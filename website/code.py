from llama_index import SimpleDirectoryReader, GPTListIndex, readers, LLMPredictor, PromptHelper, GPTTreeIndex
from llama_index.indices.vector_store import GPTSimpleVectorIndex
from llama_index.playground import Playground
from langchain import OpenAI
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import PyPDF2
import requests
import pandas as pd
import os
from IPython.display import Markdown, display 
import sys
from .models import Input, Response, User, Payer, Chouse, PayerID
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
import csv
import tabula as tb


def construct_index(directory_path):
  # set maximum input size
  max_input_size = 4096
  # set number of output tokens
  num_outputs = 256
  # set maximum chunk overlap
  max_chunk_overlap = 20
  # set chunk size limit
  chunk_size_limit = 600
  
  
  
  prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)

  # define LLM
  llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-ada-001", max_tokens=num_outputs))
  
  documents = SimpleDirectoryReader(directory_path).load_data()
  
  index = GPTSimpleVectorIndex.from_documents(documents)
  
  index.save_to_disk('index.json')
  
  
  return index

def ask_ai(text_data, text_id):
    #constructs new index json to use
    os.environ["OPENAI_API_KEY"] = ""
    save=r"C:\Users\gabriel.martin\Documents\GetLab\GPT_App\index.json"
    index = GPTSimpleVectorIndex.load_from_disk(save_path=save)
    while True: 
        query = text_data
        if text_logic(query) == True:
            print("hi")
            return False
                
        else:
            AI_response = "temp"
            #AI_response = index.query(query, response_mode="compact")
            #response = str(AI_response)#convert response to string
            #add a security ck here against competetor info before showing response
            if AI_response:
                if current_user.is_authenticated:
                    new_response = Response(data=AI_response, input_id=text_id)  #providing the schema for the response 
                    db.session.add(new_response) #adding the response to the database 
                    db.session.commit()
                else: #location for temp user
                    #new_text = Input(data=text)
                    #db.session.add(new_text)
                    #db.session.commit()
                    flash('Text added to temp cache!', category='success')
            if not AI_response:
                flash('Cant answer your question', category='error')
                return False
        return jsonify({})
        
        
def import_docs(q_link):
    
    #location of directory to save files
    output_dir = '.\context_data/Outputs'
    
    file_name = os.path.basename(q_link)
    file_path = os.path.join(output_dir, file_name)
    #check if file exist in output directory
    if os.path.exists(file_path):
        print(f"{file_name} already exists in {output_dir}")
        return
    response = requests.get(q_link) #get website information 
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content) #write the file to the directory with the new file location and the contents from the website
            print(f"{file_name} downloaded and saved to {output_dir}")
    else:
        print(f"Error downloading {file_name}. Status code: {response.status_code}")
            
            
def domain_ck(q_link):
   # this list is for websites to download from
    allowed_urls = ["https://cms.officeally.com/formsmanuals"]
    allowed_domains = [] 
    file_extensions = ["pdf", "doc", "docx"]
    links = []
    #cur_domain = urlparse(query).netloc # getting string after http and before and including .com
    for url in allowed_urls:
        domain = urlparse(url).netloc
        allowed_domains.append(domain)
       
        # code to get names and files from a website
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        for link in soup.find_all("a"):
            href = link.get("href")
            if href.startswith("http") and any(href.endswith(ext) for ext in file_extensions):
                name = link.text.strip()
                links.append((name, href))
            
    has_query = any(q_link in s for s in links)
    return has_query

def text_logic(query):
    #check the user input questions for key words
    key_word = ["help", "https", "more info"]
    for word in key_word:
        if word in query:
            if word == 'help':
                #ask ai
                print("stop")
                return True
            if word == 'https':
                pattern = re.compile(r'(https?://\S+)')
                match = pattern.search(query)
                if match is not None:
                    q_link = match.group(1)
                    if domain_ck(q_link) == True:
                        import_docs(q_link)
                        construct_index('context_data\Outputs')
                        return True
                    else:
                        print(f"{q_link} is not from an approved doamin")
                        return True #will be removed apon farther logic
    return False   
            

def extact_url(query):
    pattern = re.compile(r'(https?://\S+)')
    match = pattern.search(query)
    if match is not None:
        return match.group(1)
        
    else:
        return None
    
    
def check_db(text):
    #cleans up database
    delete_temp()
    #pulls all input ids and corrasponding data
    input_data = db.session.query(Input.id, Input.data)
    payer_data = db.session.query(Payer.payer_name, Payer.payer_id, Payer.c_house)
    for input in input_data:
        #when it finds a match for the input it pulls the response for the input
        if input.data == text:
            response = Response.query.get(input.id)
            response = response.data
            return response
    #check and find out if input is refering to payer list
    for data in payer_data:
        if data.payer_name == text:
            response = [data.payer_id, data.c_house]
            return response
        elif data.payer_id == text:
            response = [data.payer_name, data.c_house]
            return response
    return None
    
     
def delete_null():
    #pulls all responses with null inputs (does not have a connecting question or input)  
    obj1_id = Response.query.filter(Response.input_id==None).all()
    print(obj1_id)
    for obj in obj1_id:
        id_res = obj.id
        if id_res == None:
            id_inp = Input.query.get(id_res)
            print(id_inp)
    
def delete_temp():
    #get all input ids
    pull_i = db.session.query(Input.id).all()
    #get all response input_ids
    pull_r = db.session.query(Response.input_id).all()
    #pulling null input_id and associating id to delete
    pull_null = db.session.query(Response.id, Response.input_id).all()
    
    input_set = set(pull_i)
    response_set = set(pull_r)
    
    matches = input_set.intersection(response_set)
    
    #delete input that has no resonse in db
    for inp_id in pull_i:
        if inp_id not in matches:
            inp_id = Input.query.get(inp_id)
            db.session.delete(inp_id)
            db.session.commit()
    #check and delete response data that has no input    
    for res_id in pull_null:
        res_inp_id = res_id.input_id
        if res_inp_id == None:
            #after comfirming null is in input_id get the data and delete
            res_id = Response.query.get(res_id.id)
            db.session.delete(res_id)
            db.session.commit()
            
            
def payer_add(payer_list):
    data = pd.read_csv(payer_list, sep=':')
    records = data.to_dict('records')
    for record in records:
        c_house = Chouse.query.filter_by(c_name=record['house name']).first()
        if c_house:
            # If the CHouse object already exists in the database, associate it with the payer
            existing_payer = Payer.query.filter_by(payer_name=record['payer name']).first()
            if existing_payer:
                # If the payer with the same name already exists, update its payer_id
                payer_id = PayerID(payer_id=record['payer id'])
                existing_payer.payer_ids.append(payer_id)
            else:
                # If the payer with the same name does not exist, create a new one and associate it with the CHouse
                payer = Payer(payer_name=record['payer name'], c_house=c_house)
                payer_id = PayerID(payer_id=record['payer id'], payer=payer)
                payer.payer_ids.append(payer_id)
                db.session.add(payer)
        else:
            # If the CHouse object does not exist in the database, create a new one and associate it with the payer
            c_house = Chouse(c_name=record['house name'])
            db.session.add(c_house)
            payer = Payer(payer_name=record['payer name'], c_house=c_house)
            payer_id = PayerID(payer_id=record['payer id'], payer=payer)
            db.session.add(payer_id)
            db.session.add(payer)
    db.session.commit()


def file_choice():
    cur_dir = os.path.abspath(path=r"C:\Users\gabriel.martin\Documents\GetLab\GPT_App\context_data\payer_list")
    files = os.listdir(cur_dir)
    print(files)
    choice = int(request.form.get('input'))
    if choice:
        my_path = os.path.join(cur_dir, files[choice])
        if my_path.endswith("xlsx"):
            excel_payer(cur_dir, file=my_path)
        elif my_path.endswith("pdf"):
            pdf_payer(cur_dir, file=my_path)
        else:
            print("no file conversion created")
        
    
    
    
def excel_payer(cur_dir, file):
    
    exc_path = os.path.join(cur_dir, file)
    print(exc_path)
    dfs = pd.read_excel(exc_path, nrows=10000)
    headers = [header.lower() for header in dfs.columns] #pull headers and set them lower case
    for header in headers:
        if header == "payer code": #make sure all cases are using payer name or payer id as columns
            temp = headers.index(header)
            headers.insert(temp,"payer id")
            headers.remove(header)
    dfs.columns = headers
    
    
    payer_list = os.path.join(cur_dir, "CSV", "output.csv")
    dfs[['payer name', 'payer id']].to_csv(payer_list, index=False, sep=':')
    print(payer_list)
    data = pd.read_csv(payer_list, sep=':')
    df = pd.DataFrame(data)
    df = df.dropna()
    files = os.listdir(cur_dir)
    choice = int(request.form.get('input'))
    file = files[choice]
    company = file.split()[0]
    
    #company = str(input("clearing house name"))
    df['house name'] = company
    df.to_csv(payer_list, index=False, sep=':')
    payer_add(payer_list=payer_list)
    
def pdf_payer(cur_dir, file):
    
    pdf_path = os.path.join(cur_dir, file)
    dfs = tb.read_pdf(pdf_path, pages='all', java_options="-Xmx4096m", encoding="latin1")
    df = pd.concat(dfs)
    temp_file = os.path.join(cur_dir, "temp.xlsx")
    df.to_excel(temp_file)
    excel_file = 'temp.xlsx'
    excel_payer(cur_dir, file = excel_file)