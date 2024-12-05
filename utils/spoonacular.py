import requests
from openai import AzureOpenAI
import os

client = AzureOpenAI(
    api_key = os.getenv("AZURE_KEY"),
    api_version = "2024-03-01-preview",
    azure_endpoint = os.getenv("AZURE_ENDPOINT")
)


def load_api_key():
    with open("spoonacularAPI_Key.txt", 'r') as file:
        return file.read()

def get_recipes(ingredients):
    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&apiKey={API_KEY}"
    response = requests.get(url)
    return response.json()

def get_recipe_details(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={API_KEY}"
    response = requests.get(url)
    return response.json()

#OPENAI.PY

def generate_instructions(recipe_details):
    prompt = f"Generate step-by-step instructions for {recipe_details['title']}."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200
    )
    return response.choices[0].text.strip()

def generate_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    return response['data'][0]['url']