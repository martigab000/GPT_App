from llama_index import SimpleDirectoryReader, GPTListIndex, readers, LLMPredictor, PromptHelper, GPTTreeIndex
from llama_index.indices.vector_store import GPTSimpleVectorIndex
from llama_index.playground import Playground
from langchain import OpenAI
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import PyPDF2
import requests
import sys
import os
from IPython.display import Markdown, display 
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

def construct_index(directory_path):
  # set maximum input size
  max_input_size = 4096
  # set number of output tokens
  num_outputs = 256
  # set maximum chunk overlap
  max_chunk_overlap = 20
  # set chunk size limit
  chunk_size_limit = 600
  
  os.environ["OPENAI_API_KEY"] = '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'
  
  prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)

  # define LLM
  llm_predictor = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-ada-001", max_tokens=num_outputs))
  
  documents = SimpleDirectoryReader(directory_path).load_data()
  
  index = GPTSimpleVectorIndex.from_documents(documents)
  
  index.save_to_disk('index.json')
  
  
  return index

def ask_ai(text_data):
    construct_index('context_data\Outputs')
    index = GPTSimpleVectorIndex.load_from_disk('index.json')
    while True: 
        query = text_data
        print(text_data)
        print(query)
        if text_logic(query) == True:
            print("hi")
            return False
                
        else:
            AI_response = index.query(query, response_mode="compact")
            #add a security ck here against competetor info before showing response
            
            #display(Markdown(f"Response: <b>{AI_response.response}</b>"))
            return False
        
        
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
                        return True
                    else:
                        print("{q_link} is not from an approved doamin")
                        return True #will be removed apon farther logic
    return False   
            

def extact_url(query):
    pattern = re.compile(r'(https?://\S+)')
    match = pattern.search(query)
    if match is not None:
        return match.group(1)
        
    else:
        return None