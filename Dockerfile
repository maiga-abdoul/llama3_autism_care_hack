FROM python:3.9-slim-buster

WORKDIR /Auti_Care_App

COPY requirements.txt .
COPY main.py .
COPY rag_handler.py .
COPY autism_caregiving_data.pdf .
COPY autiCare.png .

COPY Dockerfile .


RUN pip install --upgrade pip
RUN pip install deep-translator 
RUN pip install langchain 
RUN pip install langchain_core 
RUN pip install langchain_openai 
RUN pip install streamlit
RUN pip install langchain_community 



# EXPOSE 8080

CMD ["streamlit", "run", "main.py"]