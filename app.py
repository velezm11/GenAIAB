# Do a similarity search for user input to documents ( embeddings) in OpenSearch
import sys
import os
import boto3
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
from requests_aws4auth import AWS4Auth
from langchain.chains import RetrievalQA                       
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
from opensearchpy import RequestsHttpConnection
import json


def get_bedrock_client():
    bedrock = boto3.client('bedrock-runtime')
    return bedrock

def create_langchain_vector_embedding_using_bedrock(bedrock_client):
    bedrock_embeddings_client = BedrockEmbeddings(
        client=bedrock_client,
        model_id="amazon.titan-embed-text-v1")
    return bedrock_embeddings_client
    

def create_opensearch_vector_search_client(indexName, bedrock_embeddings_client, opensearch_endpoint, _is_aoss=False):
    aws_region = "us-east-1"
    #OpenSearch Auth
    service = 'aoss'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, aws_region, service, session_token=credentials.token)


    docsearch = OpenSearchVectorSearch(
        index_name=indexName,
        embedding_function=bedrock_embeddings_client,
        opensearch_url="cb97nvmsmyyx5gwdz5d0.us-east-1.aoss.amazonaws.com",
        http_auth=awsauth,
        is_aoss=_is_aoss,
        timeout=300,
        use_ssl = True,
        verify_certs = True,
        engine="faiss",
        connection_class = RequestsHttpConnection
    )
    return docsearch


def create_bedrock_llm(bedrock_client):
    bedrock_llm = Bedrock(
        model_id="anthropic.claude-v2:1", 
        client=bedrock_client,
        #model_kwargs={'temperature': 0.5, 'maxTokens':8191, "topP":0.8}
        )
    return bedrock_llm
    

def lambda_handler(event, context):
    aws_region = "us-east-1"
    #OpenSearch Auth
    service = 'aoss'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, aws_region, service, session_token=credentials.token)


    try:
        try:
            '''           
            print(event)
            body = json.loads(event['body'])
            question = body["question"]
            '''

            print("Received event:", event)  # This will show the complete event structure

            # Assuming event['body'] is a JSON string.
            body_str = event['body']
            print("Body as string:", body_str)  # This should show the JSON string

            body = json.loads(body_str)  # This converts the JSON string to a Python dictionary.
            print("Body as dict:", body)  # This will show the dictionary structure

            question = body["question"]
            print("Question:", question)  # This will show the extracted question
        except Exception as e:
            print(e)    

        region = "us-east-1"
        indexName = "hybrid-search" 
        

        bedrock_client = get_bedrock_client()
        bedrock_llm = create_bedrock_llm(bedrock_client)
        
        bedrock_embeddings_client = create_langchain_vector_embedding_using_bedrock(bedrock_client)
        

        opensearch_endpoint = "/opensearch/domainEndpoint"
        opensearch_vector_search_client = create_opensearch_vector_search_client(indexName, bedrock_embeddings_client, opensearch_endpoint)
        
        # LangChain prompt template
        question = question
        
        prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. don't include harmful content
        {context}

        Question: {question}
        Answer:"""
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        
        qa = RetrievalQA.from_chain_type(llm=bedrock_llm, 
                                         chain_type="stuff", 
                                         retriever=opensearch_vector_search_client.as_retriever(), #search_type = "similarity", search_kwargs = { "k": 23 }
                                         return_source_documents=True,
                                         chain_type_kwargs={"prompt": PROMPT, "verbose": True}, 
                                         verbose=True) 
    
        res = qa(question, return_only_outputs=False)
        
        print(res)
            
        result = {
            "query": res['query'],
            "answer": res['result'],
            "document Source": str(res['source_documents'])
        }
        
        response = {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except json.JSONDecodeError:
        response = {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid Json"})
        }
    
    return response
