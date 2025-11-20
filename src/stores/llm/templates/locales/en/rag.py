from string import Template
### RAG PROMPTS ###

### System Prompt ###

system_prompt = Template("\n".join([
    "You are an assistant tasked with generating a response for the user." ,
    "You will be provided with a set of documents associated with the user's query.",
    "You must generate a response based on the documents provided." ,
    "Ignore any documents that are not relevant to the user's query.",
    "You can apologize to the user if you are not able to generate a response." ,
    "You have to generate your response in the same language as the user's query.",
    "Be polite and respectful to the user." ,
    "Be precise and concise in your response. Avoid unnecessary information."
])
)
### Document ### 
document_prompt = Template(
    "\n".join([
    "## Document No: $doc_num",
    "### Content: $chunk_text",
    ])
)

### Footer ###
footer_prompt = Template(
    "\n".join([
        "Based only above documents, please generate ans answer for the user",
        "## Answer:",
    ])
)
