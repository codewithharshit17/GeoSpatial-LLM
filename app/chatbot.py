from langchain.llms import HuggingFacePipeline
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Load Mistral model from /models/mistral
model_path = "models/mistral"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=200)

llm = HuggingFacePipeline(pipeline=pipe)

prompt = PromptTemplate(
    input_variables=["query"],
    template="""
You are an expert geospatial analyst. The user will ask about heatwave trends in Mumbai from satellite and census data.
Think step-by-step and give a clear answer.

User: {query}
""")

chain = LLMChain(llm=llm, prompt=prompt)
