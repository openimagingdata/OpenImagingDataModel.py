"""Use OpenAI's GPT models to automatically generate a Finding Model from a text representation of the model."""

from os import getenv

from dotenv import load_dotenv
from instructor import from_openai
from openai import AsyncOpenAI

from .finding_model import FindingModel

PROMPT = [
    {
        "role": "system",
        "content": """You are a radiology informatics assistant helping a radiologist generate structured
            representations of radiologist findings. You are very good at understanding the properties of
            radiology findings that radiologists use in their reports and can propose what the allowed
            attributes of the description of a finding would be along with the data type and allowed value.""",
    },
    {
        "role": "system",
        "content": """Note that the allowed types of attributes are 'choice' and 'numeric'. For text-based
            attributes, use 'choice' and provide a list of possible values. For example, for a finding that has
            a severity attribute, the type would be 'choice' and the values might be 'mild', 'moderate', and 
            'severe'.""",
    },
    {
        "role": "system",
        "content": """For numeric attributes, use 'numeric' and provide a range of allowed values and the
            relevant unit. For example, for a finding that has a size attribute, the type would be 'numeric'
            and the range might be 1-10 cm.""",
    },
    {
        "role": "user",
        "content": """A radiologist expert has created an outline for how radiologists describe a finding 
                would describe a finding in their radiology report. The outline includes the different attributes
                used and where possible information on what acceptable values for those are.""",
    },
    {
        "role": "user",
        "content": """Please review the expert's outline and convert it into the appropriate format 
                according to the function signature. If something isn't clear from the outline, make a best/default 
                guess at the value so that the model can be created.""",
    },
]


async def text_to_finding_model(expert_text: str) -> FindingModel:
    load_dotenv()
    openai = AsyncOpenAI(api_key=getenv("OPENAI_API_KEY"))
    client = from_openai(openai)
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=PROMPT
        + [
            {
                "role": "user",
                "content": f"""Expert's outline: 
                ```
                {expert_text}
                ```""",
            }
        ],
        response_model=FindingModel,
    )
    return response
