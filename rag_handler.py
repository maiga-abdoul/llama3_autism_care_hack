from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from deep_translator import GoogleTranslator
# from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader

translator = GoogleTranslator(source='en', target='swahili')

def translate(text, target_language):
    if target_language == 'en':
        return text
    return translator.translate(text, target_lang=target_language)


def load_pdf_chunks(pdf_file):
   
    loader = PyPDFLoader(pdf_file)
    pages = loader.load_and_split()

    return pages #documents


def process_query(api_key:str='', query: str='', pdf_file:str='', language:str='en'):
    # Initialize OpenAI with the provided API key
    OPENAI_API_KEY = api_key
    print('other api key', OPENAI_API_KEY)
    model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-4o")

    # use StrOutputParser to extract the answer as a string
    parser = StrOutputParser()
    # chain = model | parser

    # define the prompt template
    template = """
   you are an assistant in all topics related to autism and taking care of people with autism at Kenya Institute of Special Education (KISE). your name is
   "Auti-Care Chatbot".
    Answer the user question in details based on the context below combined with your own expertise and if the context do not provide enough information,
    you can complete the response with your own knowledge.
    If you can't answer the user question from the context, answer the question base on your expertise and highlith it. 
    you can answer to only questions related to autism.

    Context: {context}

    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)
    
    # call a function that take a pdf as question then process it and return chnunks
    documents = load_pdf_chunks(pdf_file)

    # Embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    # Set up a vector store and new chain
    vectorstore = DocArrayInMemorySearch.from_documents(documents, embeddings)
    chain = (
    {"context": vectorstore.as_retriever(), "question": RunnablePassthrough()}
    | prompt
    | model
    | parser
        )
    
    response = chain.invoke(f"the query is the following and if it is hard to understand, reformulate it well before answering to it. the output must always be only the answer: {query}")
    if language == 'swahili':
        response = translate(text=response, target_language = language)
        return response
    else:
        return response

