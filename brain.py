import os
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage
from prompts import *

class AiSuggestionOutput(BaseModel):
    ai_suggestion: str = Field()

class Brain:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.5,
            api_key = os.environ.get("GEMINI_API_KEY", "")
        ).with_structured_output(AiSuggestionOutput)

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system",system_prompt),
            ('human',example_forecast),
            AIMessage(content=example_response),
            ("human", "{forecast}")])

    def ai_suggestion(self,forecast_str:str)->str:
        chain = self.prompt_template | self.llm
        response = chain.invoke({"forecast": forecast_str})
        return response
