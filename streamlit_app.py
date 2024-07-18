import streamlit as st
import rag_handler
# from langchain_helper import process_query
import os
from deep_translator import GoogleTranslator


# Define a function to load the API key from the session
@st.cache_data(show_spinner=False)
def load_api_key():
    return st.session_state['api_key']

# Set the background colors
page_bg_color = """
<style>
header {visibility: hidden;}
.main {
    background-color: ##00011F; /* Replace with your desired color code */
}
[data-testid="stSidebar"] > div:first-child {
    background-color: #0A0608; /* Replace with your desired color code */
}
</style>
"""

# Render the CSS styles
st.markdown(page_bg_color, unsafe_allow_html=True)

@st.cache_resource
def initialize():
    chat= rag_handler
    return chat

st.session_state.chat=initialize()


# Set up session state for language
if 'language' not in st.session_state:
    st.session_state.language = 'english'

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []



# translation function
def translate_text(text, language):
    
    if st.session_state.language == "swahili":
        translator = GoogleTranslator(source="english", target="swahili")
        return translator.translate(text)
    return text

# translation function
def translate_prompt(text, language):
    
    if language == "swahili":
        translator = translator = GoogleTranslator(source="swahili", target="english")
        # print("translated",translator.translate(text))
        return translator.translate(text)
    return text

# Function to translate all text in the app
def get_translated_texts(language):
    texts = {
    'english': {
        'title': 'Autism Counseling Assistant',
        'settings': 'Settings',
        'choose_language': 'Choose Language',
        'enter_api': 'enter you openai api key',
        'processing': 'Processing...',
        'upload_pdf': 'Upload a PDF',
        'spinning': 'Processing...',
        'input_message': 'Enter your query here...',
        'submit':'submit',
        'api_key_error': 'Please enter your OpenAI API key in the sidebar.',
        'verify_api_message': 'Please verify that your OpenAI API key in the sidebar is correct.',
        'api_success': 'API key submitted successfully!',
        'chatbot': 'AUTI-CARE smart chatbot'
    },
    'swahili': {
        'title': 'Msaidizi wa Ushauri wa Autism',
        'settings': 'Mipangilio',
        'choose_language': 'Chagua Lugha',
        'enter_api': 'ingiza ufunguo wa openai api',
        'processing': 'Inasindika...',
        'upload_pdf': 'Pakia PDF',
        'spinning': 'Inasindika...',
        'input_message': 'Ingiza swali lako hapa...',
        'submit':'wasilisha',
        'api_key_error': 'Tafadhali ingiza kitufe chako cha OpenAI API kwenye upau wa kando.',
        'verify_api_message': 'Tafadhali thibitisha kuwa ufunguo wako wa OpenAI API katika utepe ni sahihi.',
        'api_success': 'Ufunguo wa API umewasilishwa!',
        'chatbot': 'AUTI-CARE chatbot mahiri'
    }
        }

    return texts[st.session_state.language]

# Language selection
language = st.sidebar.selectbox("Choose Language", ("english", "swahili"))
if language == 'swahili':
    st.session_state.language = 'swahili'
else:
    st.session_state.language = 'english'

# Get translated texts based on the selected language
texts = get_translated_texts(st.session_state.language)


# Function to handle the API key submission
# @st.cache_data(show_spinner=False)
def handle_submit(api_key):
    if api_key:
        st.session_state['api_key'] = api_key
        # print(st.session_state['api_key'])
        st.sidebar.success(texts['api_success'])
        # st.sidebar.write(f"API Key: {api_key}")  # Optionally display the API key
    else:
        st.sidebar.error("Please enter a valid API key.")

# Load the image file
image_file = 'autiCare.png'

col1, col2,_ = st.columns([1, 2, 1])  # Create three columns with different widths

with col2:
  # Define the caption color (replace with "orange" for orange caption)
  caption_color = "orange"
  
  # Display the image separately
  st.image(image_file, width=220)
  # Display the caption with HTML formatting using markdown
  st.markdown(f"<span style='color:{caption_color}'>{texts['chatbot']}</span>", unsafe_allow_html=True)


st.title(texts['title'])


# Bordered box container
with st.sidebar.container():
    st.sidebar.markdown('<div class="boxed">', unsafe_allow_html=True)

    # Input field for the API key
    api_key = st.sidebar.text_input(texts['enter_api'], type="password")
    
    # Submission button
    if st.sidebar.button(texts['submit']):
        handle_submit(api_key)

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Load the API key from the session
# api_key = load_api_key()
print('get api', api_key)

# PDF upload
uploaded_file = st.sidebar.file_uploader(texts['upload_pdf'], type=["pdf"])

# verify if a file have been uploaded. If not, we use a default file
if uploaded_file == None:
    uploaded_file = 'autism_caregiving_data.pdf'
else:
    uploaded_file = uploaded_file.name

# Main page ###################################################################################################
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
if 'api_key' in st.session_state:
    # React to user input
    if prompt := st.chat_input(texts['input_message']):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            # querry 
            with st.spinner(texts['spinning']):
                if st.session_state.language !='english':
                    prompt = translate_prompt(prompt, 'swahili')

                response = st.session_state.chat.process_query(
                    api_key=st.session_state['api_key'],
                    query=prompt,
                    pdf_file=uploaded_file,
                    language=language
                ) 
            
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response, unsafe_allow_html=True)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
        except:
            st.error(texts['verify_api_message'])
else:
    st.error(texts['api_key_error'])
