import os
import json

from app.langgraph.state_schema import State

from app.langgraph.common import chat_model
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

class Answer(BaseModel):
    ratoionale: str = Field(
        description="Think out loud and step by step to answer the question"
    )
    answer: str = Field(
        description="The answer to the question"
    )

def answer_middle_step_question(state: State) -> State:
    print("==>> answer_middle_step_question node started")
    middle_step = state["middle_step"]

    prompt = ChatPromptTemplate.from_template(
        """
Based on the retrieved code snippets, answer the following question. 
<questions>
{question}
</questions>

<code_snippets>
{retrieved_chunks}
</code_snippets>
"""
    )

    chain = prompt | chat_model.with_structured_output(Answer)

    response = chain.invoke(
        {
            "question": middle_step["prompt"],
            "retrieved_chunks": state["retrieved_chunks"],
        }
    )

    print("response: ", response)
    answer = response.answer
    print(f"==>> answer: {answer}")

    return {
        "answered_middle_steps": [
            {
                **middle_step,
                "answer": answer,
            }
        ]
    }
