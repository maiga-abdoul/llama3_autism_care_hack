class AutismTestBase:

    def __init__(self, name: str, questions: list, answers_options: list, description: str = None,
                 initial_score: float = 0):
        self.name = name
        self.description = description
        self.questions = questions
        self.answers_options = answers_options
        self.score = initial_score
        # self.test_decision = None

    def add_to_score(self, val: float) -> None:
        self.score += val

    def get_score(self) -> float:
        return self.score


