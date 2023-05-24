from llama_index import SimpleDirectoryReader, LLMPredictor, ServiceContext
from llama_index.indices.vector_store import GPTSimpleVectorIndex
from langchain.chat_models import ChatOpenAI
from langchain import SQLDatabase, SQLDatabaseChain
import os
from .models import Input, Response
from flask import flash, jsonify
from flask_login import current_user
from . import db

# key = "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"
# llm = ChatOpenAI(temperature=0, openai_api_key=key)
# sqlite_db_path = r"C:\Users\gabriel.martin\OneDrive - Office Ally Inc\Documents\GetLab\GPT_App\instance\database.db"
# temp = SQLDatabase.from_uri(f"sqlite:///{sqlite_db_path}")
# db_chain = SQLDatabaseChain(llm=llm, database=temp, verbose=True)
# db_chain.run("What is the most common payer code")


def construct_index(directory_path):
  # set maximum input size
  max_input_size = 4096
  # set number of output tokens
  num_outputs = 256
  # set maximum chunk overlap
  max_chunk_overlap = 20
  # set chunk size limit
  chunk_size_limit = 600
  
  
  
  #prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)

  # define LLM
  llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0.4, model_name="text-ada-001", max_tokens=256))
  service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, chunk_size_limit=512)
  
  documents = SimpleDirectoryReader(directory_path).load_data()
  
  index = GPTSimpleVectorIndex.from_documents(documents, service_context=service_context)
  
  index.save_to_disk('index.json')
  
  
  return index

def ask_ai(text_data, text_id):
    #constructs new index json to use
    os.environ["OPENAI_API_KEY"] = "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"
    #construct_index(directory_path=r"C:\Users\gabriel.martin\OneDrive - Office Ally Inc\Documents\GetLab\GPT_App\context_data\Outputs")
    save=r"C:\Users\gabriel.martin\OneDrive - Office Ally Inc\Documents\GetLab\GPT_App\index.json"
    index = GPTSimpleVectorIndex.load_from_disk(save_path=save)
    while True: 
        query = text_data
        # if text_logic(query) == True:
        #     print("hi")
        #     return False
                
        
        #AI_response = "temp"
        AI_response = index.query(query, response_mode="compact")
        response = str(AI_response)#convert response to string
        #add a security ck here against competetor info before showing response
        if AI_response:
            if current_user.is_authenticated:
                new_response = Response(data=response, input_id=text_id)  #providing the schema for the response 
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

