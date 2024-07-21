from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from deep_translator import GoogleTranslator
# from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from openai import OpenAI
import os
from together import Together

translator = GoogleTranslator(source='en', target='swahili')


def translate(text, target_language):
    if target_language == 'en':
        return text
    return translator.translate(text, target_lang=target_language)


def load_pdf_chunks(pdf_file):
    loader = PyPDFLoader(pdf_file)
    pages = loader.load_and_split()

    return pages  # documents


def process_query(api_key: str = '', query: str = '', pdf_file: str = '', language: str = 'en'):
    # Initialize OpenAI with the provided API key
    OPENAI_API_KEY = api_key
    # print('other api key', OPENAI_API_KEY)
    model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

    # use StrOutputParser to extract the answer as a string
    parser = StrOutputParser()
    # chain = model | parser

    # define the prompt template
    template = """
    You are a supportive and knowledgeable assistant designed to help parents of children with autism. Your role is to provide evidence-based information, practical advice, and emotional support to these parents. When responding to queries, follow these guidelines:
    Be empathetic and understanding of the challenges parents face.
    Provide clear, concise, and actionable advice based on current best practices in autism care and support.
    Emphasize the importance of professional diagnosis and intervention.
    Encourage parents to work closely with healthcare providers, therapists, and educators.
    Offer strategies for managing common challenges associated with autism, such as communication difficulties, sensory sensitivities, and behavioral issues.
    Promote the child's strengths and unique abilities, not just focusing on challenges.
    Suggest resources for further learning and support, such as reputable organizations, support groups, and educational materials.
    Remind parents to take care of their own well-being and seek support when needed.
    Be culturally sensitive and adaptable to different family situations.
    Clarify that while you can provide general information, specific medical or therapeutic advice should come from qualified professionals.
    When a parent asks a question or describes a situation, respond with:
    A brief acknowledgment of their situation
    Relevant, evidence-based information or advice
    Practical strategies or tips they can implement
    Encouragement and support
    A suggestion for professional help or additional resources if appropriate
    Remember, every child with autism is unique. Encourage parents to celebrate their child's individuality while providing the support and resources they need to thrive. 


    Context: {context}

    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    # call a function that take a pdf as question then process it and return chunks
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

    response = chain.invoke(
        f"the query is the following and if it is hard to understand, reformulate it well before answering to it. the output must always be only the answer: {query}")
    if language == 'swahili':
        response = translate(text=response, target_language=language)
        return response
    else:
        return response


def query_should_we_display_test(api_key: str = '', query: str = ''):
    # Initialize OpenAI with the provided API key
    OPENAI_API_KEY = api_key
    # print('other api key', OPENAI_API_KEY)
    model = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

    # use StrOutputParser to extract the answer as a string
    parser = StrOutputParser()
    # chain = model | parser

    # define the prompt template
    template = """
    You are an AI assistant helping parents of children with autism. Your task is to determine if a user's query indicates they want to test their child for signs of autism. Respond with only "yes" or "no".
    Guidelines:
    
    Respond "yes" if the query:
    
    Mentions testing, screening, or evaluating for autism
    Asks about autism signs they want to evaluate, symptoms, or early indicators
    Expresses concern about their child's development in areas related to autism (e.g., social skills, communication, repetitive behaviors)
    
    
    Respond "no" for:
    
    General questions about autism
    Queries about managing autism or supporting an autistic child
    Any other topic not directly related to identifying autism in a child
    
    
    
    Remember: Only respond with "yes" or "no". Do not provide any other information or explanation.


    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    chain = (
            {"context": None, "question": RunnablePassthrough()}
            | prompt
            | model
            | parser
    )

    response = chain.invoke(
        f"{query}")
    return response


class OpenAiModel:
    def __init__(self, model: str = "", prompt: str = "", user_content: str = "", image_size: str = "1024x1024",
                 quality: str = "standard", num_images: int = 1, api_key: str = ''):
        """
        param: image_size: ['256x256', '512x512', '1024x1024', '1024x1792', '1792x1024']
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.prompt = prompt
        self.user_content = user_content
        self.image_size = image_size
        self.quality = quality
        self.num_images = num_images

    def get_message(self):

        if self.prompt == "" or self.user_content == "":
            print(f"Error: Please provide `prompt` and `user_content`")
            return None

        if "dall" in self.model:
            print(f"Error: {self.model} is only image generation not text generation.")
            return None

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": self.user_content}
            ]
        )
        print(f"completion.choices[0].message: {completion.choices[0].message.content}")
        return completion.choices[0].message.content

    def get_images_urls(self):
        if self.prompt == "" and self.user_content == "":
            print("Error: Please provide `prompt` and/or `user_content`")
            return None

        if "dall" not in self.model:
            print(f"Error: {self.model} is only text generation not image generation.")
            return None

        print(f"get_images_urls-model: {self.model}")
        print(f"guser_content: {self.user_content}")
        response = self.client.images.generate(
            model=self.model,  # "dall-e-3",
            prompt=self.user_content,
            size=self.image_size,
            quality=self.quality,
            n=self.num_images,
        )

        return response