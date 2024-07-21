import streamlit as st
import rag_handler
# from langchain_helper import process_query
import os
from deep_translator import GoogleTranslator

# Define a function to load the API key from the session
from autism_tests import MChat


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
    chat = rag_handler
    return chat


st.session_state.chat = initialize()

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
            'enter_api': 'Enter you openai api key',
            'processing': 'Processing...',
            'upload_pdf': 'Upload a PDF',
            'spinning': 'Processing...',
            'input_message': 'Enter your query here...',
            'submit': 'submit',
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
            'submit': 'wasilisha',
            'api_key_error': 'Tafadhali ingiza kitufe chako cha OpenAI API kwenye upau wa kando.',
            'verify_api_message': 'Tafadhali thibitisha kuwa ufunguo wako wa OpenAI API katika utepe ni sahihi.',
            'api_success': 'Ufunguo wa API umewasilishwa!',
            'chatbot': 'AUTI-CARE chatbot mahiri'
        }
    }

    return texts[st.session_state.language]


prompt_template = """
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
    """

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

col1, col2, _ = st.columns([1, 2, 1])  # Create three columns with different widths

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
    st.sidebar.markdown('<div class="boxed" style="color: white;">', unsafe_allow_html=True)
    st.markdown(f"<span style='color:white'>{texts['enter_api']}</span>", unsafe_allow_html=True)
    # Input field for the API key
    api_key = st.sidebar.text_input(label="Api key", type="password", label_visibility="hidden")

    # Submission button
    if st.sidebar.button(texts['submit'] or True):
        handle_submit(api_key)

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Load the API key from the session
# api_key = load_api_key()
# print('get api', api_key)

uploaded_file = 'autism_caregiving_data.pdf'

from autism_tests import AutismTest
# Main page ###################################################################################################
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



# st.session_state["autism_test"].display_test()

if "autism_test" not in st.session_state:
    st.session_state["autism_test"] = AutismTest(name="M-Chat")

if 'api_key' in st.session_state:
    open_ai_model = rag_handler.OpenAiModel(model="gpt-3.5-turbo", api_key=st.session_state['api_key'])

    # React to user input
    if prompt := st.chat_input(texts['input_message']):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = None

        with st.spinner(texts['spinning']):
            open_ai_model.prompt = prompt_template
            open_ai_model.user_content = prompt
            decision_to_display_test = open_ai_model.get_message()
            print(
                f"BEFORE: st.session_state.get('decision_to_display_test', False): {st.session_state.get('decision_to_display_test', False)}")
            if decision_to_display_test.lower() == "yes" or st.session_state.get("decision_to_display_test", False):
                st.session_state["decision_to_display_test"] = True
                # st.session_state["autism_test"].display_test()
            else:
                st.session_state["autism_test"].reset_test()
                st.session_state["decision_to_display_test"] = False

                response = st.session_state.chat.process_query(
                    api_key=st.session_state['api_key'],
                    query=prompt,
                    pdf_file=uploaded_file,
                    language="english"
                )

        # Display assistant response in chat message container
        if response is None:
            response = "Ok. Please answer the following series of questions. After that, I'll give you a result based " \
                       "the the M-Chat test grades. "
            open_ai_model.prompt = "You're an assistant who reformulates user text in the context where the user want " \
                                   "to test his or her child for autism. Reformulate the following text.. "
            open_ai_model.user_content = response
            response = open_ai_model.get_message()
        with st.chat_message("assistant"):
            st.markdown(response, unsafe_allow_html=True)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        # except BaseException as e:
        #     print(str(e))
        #     st.error(texts['verify_api_message'])

else:
    st.error(texts['api_key_error'])

if st.session_state.get("decision_to_display_test", False):
    print(
        f"00 ---- decision_to_display_test: {st.session_state.get('decision_to_display_test', False)}")
    with st.chat_message("assistant"):
        if st.session_state["autism_test"].test.get_decision() is None:
            st.session_state["autism_test"].display_test()  # Display test form
        else:
            st.session_state["autism_test"].reset_test()
            st.session_state["decision_to_display_test"] = False

test_decision = st.session_state["autism_test"].test.get_decision()
print(f"1234 --------- test_decision: {test_decision}")
print(f"1234 --------- score: {st.session_state['autism_test'].test.get_score()}")

if test_decision is not None:
    with st.spinner(texts['spinning']):
        print(f"autism_test.test.test_decision: {test_decision} --- decision_to_display_test: {st.session_state.get('decision_to_display_test', False)}")

        st.session_state["decision_to_display_test"] = False
        open_ai_model.prompt = "You're a useful assistant. You always communicate on a M-Chat test for autism " \
                               "detection in professional manner. You can also provide advice when needed. " \
                               "Always reassure the parents as needed to help prevent any anxiety or panic." \
                               "Below is the out of a M-Chat test. Communicate the result to the user."
        open_ai_model.user_content = test_decision
        response = open_ai_model.get_message()

    with st.chat_message("assistant"):
        st.markdown(response, unsafe_allow_html=True)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

    st.session_state["autism_test"].reset_test()
    st.session_state["decision_to_display_test"] = False

