import os
from typing import List, Union
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI

from schemas import WaterAssessment
from image_utils import load_and_encode_image
from prompt import SYSTEM_ASSESSMENT_PROMPT

# Load environment variables from .env
load_dotenv()



def build_multimodal_message(image_info: dict) -> List[BaseMessage]:
    """Constructs a multimodal LangChain HumanMessage containing prompt and image data URL.

    Args:
        image_info: Dictionary containing 'data_url' and 'mime_type'.

    Returns:
        List[BaseMessage]: A single-item list containing the multimodal HumanMessage.
    """
    data_url = image_info["data_url"]

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": SYSTEM_ASSESSMENT_PROMPT,
            },
            {
                "type": "image_url",
                "image_url": {"url": data_url},
            },
        ]
    )
    return [message]


def get_structured_llm() -> RunnableLambda:
    """Initializes and returns the structured output Gemini model as a runnable.

    Reads GOOGLE_API_KEY and GEMINI_MODEL from the environment at invocation time.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY environment variable is missing. "
            "Please set your Gemini API key in the .env file."
        )

    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.1,
        google_api_key=api_key,
    )
    return llm.with_structured_output(WaterAssessment)


# Core LCEL runnables
image_processing_runnable = RunnableLambda(load_and_encode_image)
prompt_runnable = RunnableLambda(build_multimodal_message)
structured_llm_runnable = RunnableLambda(lambda messages: get_structured_llm().invoke(messages))

# Composable LCEL chain: image_path -> image_processing -> multimodal_prompt -> structured_llm -> WaterAssessment
water_assessment_chain = (
    image_processing_runnable
    | prompt_runnable
    | structured_llm_runnable
)

