# Import the necessary treasures and libraries once again!
import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI  # Use the chat-based OpenAI class for GPT-4

import re  # For regex-based cleaning of filenames
import random

# Initialize yer AI brain (LLM) with increased max_tokens, and use the chat-based GPT model
llm = ChatOpenAI(model="gpt-4", temperature=0.7, max_tokens=300)  # Explicitly use gpt-4 chat model

# Define prompt templates for each tool
chapter_prompt_template = PromptTemplate(
    input_variables=["prompt"],
    template="Generate a unique concept for a new Space Marine chapter based on the following prompt: '{prompt}'. Include the chapter's purpose, ideals, and characteristics."
)

homeworld_prompt_template = PromptTemplate(
    input_variables=["chapter_concept"],
    template="Describe the homeworld of the Space Marine chapter based on this concept: '{chapter_concept}'. Include details about the environment, culture, and significance to the chapter."
)

origin_legion_prompt_template = PromptTemplate(
    input_variables=["chapter_concept"],
    template="Select a suitable origin legion for a Space Marine chapter based on this concept: '{chapter_concept}'. Provide a brief reason for the choice."
)

chapter_name_prompt_template = PromptTemplate(
    input_variables=["chapter_concept"],
    template="Extract a suitable name for the Space Marine chapter based on the following concept: '{chapter_concept}'. The name should reflect the chapter's characteristics and ideals."
)

# Create LLMChains for each tool using the chat-based model
chapter_generator = LLMChain(llm=llm, prompt=chapter_prompt_template)
homeworld_generator = LLMChain(llm=llm, prompt=homeworld_prompt_template)
origin_legion_generator = LLMChain(llm=llm, prompt=origin_legion_prompt_template)
chapter_name_generator = LLMChain(llm=llm, prompt=chapter_name_prompt_template)

# Function to handle long responses and ensure full generation with a limit on retries
def ensure_full_generation(llm_chain, input_data, max_retries=3):
    response = llm_chain(input_data)["text"]
    retries = 0  # Initialize the retry count
    
    # Detect if the response is likely truncated
    while not response.endswith(".") and retries < max_retries:  # Assuming a complete sentence ends with a period.
        print(f"Detected incomplete response, requesting more... Retry {retries + 1}/{max_retries}")
        # Continue generating by passing part of the previous response to continue
        additional_response = llm_chain({"prompt": response})["text"]
        response += additional_response  # Concatenate additional response
        retries += 1  # Increment the retry count
    
    if retries == max_retries:
        print(f"Warning: Response still incomplete after {max_retries} retries.")
    
    return response

# Function to generate chapter concepts with full text handling
def generate_chapter_concept(prompt):
    print(f"Generating chapter concept using prompt: {prompt}")
    chapter_concept = ensure_full_generation(chapter_generator, {"prompt": prompt})
    print(f"Generated chapter concept: {chapter_concept}")
    return chapter_concept

# Function to describe the homeworld with full text handling
def generate_homeworld(chapter_concept):
    print(f"Generating homeworld description for chapter concept: {chapter_concept}")
    homeworld_description = ensure_full_generation(homeworld_generator, {"chapter_concept": chapter_concept})
    print(f"Generated homeworld description: {homeworld_description}")
    return homeworld_description

# Function to generate the chapter name with full text handling
def generate_chapter_name(chapter_concept):
    print(f"Generating chapter name from the chapter concept: {chapter_concept}")
    chapter_name = ensure_full_generation(chapter_name_generator, {"chapter_concept": chapter_concept})
    print(f"Generated chapter name: {chapter_name}")
    return chapter_name

# Function to choose an origin legion (this one doesn't need truncation handling)
def choose_origin_legion(chapter_concept):
    print(f"Choosing origin legion for chapter concept: {chapter_concept}")
    legions = [
        "Ultramarines", 
        "Blood Angels", 
        "Dark Angels", 
        "Space Wolves", 
        "Imperial Fists", 
        "Iron Hands", 
        "Salamanders", 
        "Raven Guard"
    ]
    chosen_legion = random.choice(legions)
    print(f"Chosen origin legion: {chosen_legion} for concept: {chapter_concept}")
    return chosen_legion

# Function to format the final report
def format_chapter_report(chapter_concept, homeworld_description, origin_legion):
    report = (
        f"**Space Marine Chapter Overview**\n"
        f"**Chapter Concept:** {chapter_concept}\n"
        f"**Homeworld Description:** {homeworld_description}\n"
        f"**Origin Legion:** {origin_legion}\n"
    )
    print(f"Formatted chapter report:\n{report}")
    return report

# Function to clean chapter name for file system compatibility
def clean_chapter_name(chapter_name):
    # Remove any illegal characters for a filename (Windows: \ / : * ? " < > |)
    return re.sub(r'[\/:*?"<>|]', '', chapter_name)

# Function to save the chapter report to a file
def save_chapter_to_file(chapter_name, chapter_report):
    cleaned_chapter_name = clean_chapter_name(chapter_name)
    file_path = f"{cleaned_chapter_name}.txt"
    print(f"Saving chapter report to file: {file_path}")
    
    with open(file_path, 'w') as file:
        file.write(chapter_report)

# Main function to run the chapter creation process with full generation handling and retry limit
def run_space_marines_chapter_creation(prompt):
    print(f"Running Space Marines chapter creation with prompt: '{prompt}'")
    chapter_concept = generate_chapter_concept(prompt)
    homeworld_description = generate_homeworld(chapter_concept)
    origin_legion = choose_origin_legion(chapter_concept)
    
    # Determine the chapter name using LLM
    chapter_name = generate_chapter_name(chapter_concept)
    
    # Format the report
    chapter_report = format_chapter_report(chapter_concept, homeworld_description, origin_legion)
    
    # Save to file
    save_chapter_to_file(chapter_name, chapter_report)
    
    return chapter_report

# Example Run of the Chapter Creation
prompt = "A chapter devoted to the protection of ancient artifacts and knowledge."
chapter_report = run_space_marines_chapter_creation(prompt)
print(chapter_report)