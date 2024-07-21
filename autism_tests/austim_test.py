from autism_tests import MChat
import streamlit as st


class AutismTest:
    _tests_list = ["M-Chat"]

    def __init__(self, name: str, ):
        if name == "M-Chat":
            self.test = MChat()
        else:
            ValueError(
                f"Value error: {name} is not a valid test name. 'name' can only be one of these {', '.join(self._tests_list)}")

        self.name = name

        self.value = None

    def on_submit(self, val):
        self.test.add_answer(val=val)
        question_id = st.session_state["question_id"]
        print(f"{self.test.questions[question_id]} -- value: {val}")
        st.session_state["question_id"] += 1

    def get_decision(self) -> str | None:
        if st.session_state["question_id"] < len(self.test.questions):
            self.test.finish()
            return self.test.test_decision
        else:
            return None

    def reset_test(self) -> None:
        self.test.reset()
        st.session_state["question_id"] = 0

    def display_test(self) -> None:
        if "question_id" not in st.session_state:
            st.session_state["question_id"] = 0

        question_id = st.session_state["question_id"]

        _, questions_col, _ = st.columns([1, 10, 1])
        with questions_col:
            if st.session_state["question_id"] < len(self.test.questions):
                st.markdown(
                    """<h4 style="background-color: blue; text-align: center; color: white;"> M-Chat Autistm test 
                    </h4>""",
                    unsafe_allow_html=True)
                value = st.radio(options=self.test.answers_options[question_id],
                                 label=self.test.questions[question_id], key="values")
                st.button(
                    label="Next" if question_id < len(self.test.questions) - 1 else "Finish",
                    on_click=lambda: self.on_submit(value))
            else:  # Finish
                st.markdown(
                    f"""<h4 style="background-color: blue; text-align: center; color: white;">
                     {self.test.name} Test Complete 
                    </h4>""",
                    unsafe_allow_html=True)
                self.test.finish()
