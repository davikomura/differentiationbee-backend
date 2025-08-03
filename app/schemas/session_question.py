from pydantic import BaseModel

class QuestionAnswerCreate(BaseModel):
    session_id: int
    question_str: str
    correct_answer_str: str
    user_answer: str
    is_correct: bool
    time_taken: float