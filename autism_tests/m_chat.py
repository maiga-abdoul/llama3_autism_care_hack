import os
import json
from autism_tests.austim_test_base import AutismTestBase


class MChat(AutismTestBase):
    with open(os.path.join("files", "autism_test", "mchat_questions_list.json"), "r") as f:
        _questions = json.loads(f.read())[0:5]  # TODO: [0:5] must be removed

    _name = "M-Chat"
    _description = """"
        M-CHAT (Modified Checklist for Autism in Toddlers)
        Scoring: The M-CHAT has 20 yes/no questions answered by parents.
        Scoring Interpretation: Each "yes" or "no" answer is scored based on whether it indicates a risk of ASD.
    """

    _answers_options = [["Yes", "No"]]*len(_questions)

    def __init__(self):
        super().__init__(self._name, self._questions, self._answers_options)
        self.test_decision = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def questions(self) -> list:
        return self._questions

    @property
    def answers_options(self) -> list:
        return self._answers_options

    @name.setter
    def name(self, value: str):
        self._name = value

    @questions.setter
    def questions(self, value: list):
        self._questions = value

    @answers_options.setter
    def answers_options(self, value: list):
        self._answers_options = value

    def add_answer(self, val: str) -> None:
        if val == "Yes":
            self.score += 1

    def reset(self) -> None:
        self.score = 0
        self.test_decision = None

    def _make_decision(self):
        """
        Low Risk: Score of 0-2. No follow-up needed unless there are other concerns.
        Medium Risk: Score of 3-7. Follow-up with the M-CHAT-R/F (a structured follow-up interview) to determine if a full evaluation is needed.
        High Risk: Score of 8-20. Immediate referral for a comprehensive developmental evaluation.
        :return:
        """
        decision_list = ["Low Risk: No follow-up needed unless there are other concerns.",
                         "Medium Risk: Follow-up with the M-CHAT-R/F (a structured follow-up interview) to determine if a full evaluation is needed.",
                         "High Risk: Immediate referral for a comprehensive developmental evaluation."
                         ]
        if self.score <= 2:
            self.test_decision = decision_list[0]
        elif self.score <= 7:
            self.test_decision = decision_list[1]
        else:
            self.test_decision = decision_list[2]

    def finish(self):
        self._make_decision()
        print(f"finish-------------------- decision: {self.test_decision} ------- score: {self.score}")

    def get_decision(self) -> str:
        return self.test_decision
