from openai import AzureOpenAI
import os
import requests
import json
import pandas as pd

client = AzureOpenAI(
	api_key = os.getenv("AZURE_KEY"),
	azure_endpoint = os.getenv("AZURE_ENDPOINT"),
	api_version = "2023-10-01-preview"
)

def load_api_key():
	with open("spoonacularAPI_Key.txt", 'r') as file:
		return file.read()

#1.Ingredient Selection

def get_recipe(ingredients):
	api_key = load_api_key()
	response = requests.get(
		"https://api.spoonacular.com/recipes/findByIngredients",
		params={"ingredients": ingredients, "number": 3, "apiKey": api_key}
	)
	if response.status_code == 200:
		return [
			f"Recipe: {recipe['title']} | URL: https://spoonacular.com/recipes/{recipe['id']}"
			for recipe in response.json()
		]

#2.Custom Recipe Creation

def get_recipes_by_diet(self, diet, exclude, maxReadyTime):
	response = requests.get(
		"https://api.spoonacular.com/recipes/complexSearch",
		params={
			"diet": diet,
			"intolerances": exclude,
			"maxReadyTime": maxReadyTime,
			"number": 3,
			"apiKey": self.api_key
		}
	)
	if response.status_code == 200:
		 return response.json()['results']
	return None

#3. Nutritional Analysis
def get_recipe_nutrition(self, recipe_id):
	response = requests.get(
		f"https://api.spoonacular.com/recipes/{recipe_id}/nutritionWidget.json",
		params={"apiKey": self.api_key}
	)
	if response.status_code == 200:
		 return response.json()
	return None

def visualize_nutrition(self, nutrition_data):
	nutrients = ['calories', 'protein', 'fat', 'carbs']
	values = [
		float(nutrition_data['calories'].rstrip(' kcal')),
		float(nutrition_data['protein'].rstrip('g')),
		float(nutrition_data['fat'].rstrip('g')),
		float(nutrition_data['carbs'].rstrip('g'))
	]
	 
	plt.figure(figsize=(10, 6))
	plt.bar(nutrients, values)
	plt.title('Nutritional Information')
	plt.ylabel('Amount')
	plt.show()


 # 4. Step-by-Step Instructions
def get_recipe_instructions(self, recipe_id):
	response = requests.get(
		f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions",
		 params={"apiKey": self.api_key}
	)
	if response.status_code == 200:
		return response.json()
	return None

def generate_recipe_image(self, recipe_description):
	response = self.client.images.generate(
		model="dall-e-3",
		prompt=f"A professional food photo of {recipe_description}",
		n=1
	)
	return response.data[0].url

def process_user_request(self, user_input):
	messages = [
		{"role": "system", "content": "You are a helpful recipe assistant."},
		{"role": "user", "content": user_input}
	]
	 
	response = self.client.chat.completions.create(
		model="GPT-4",
		messages=messages
	)
	 
	return response.choices[0].message.content

def main():
		bot = RecipeBot()
 
while True:
	print("\nRecipe Bot Menu:")
	print("1. Search recipes by ingredients")
	print("2. Create custom recipe")
	print("3. Get nutritional analysis")
	print("4. Get cooking instructions")
	print("5. Exit")
	
	choice = input("Enter your choice (1-5): ")
	 
	if choice == '1':
		ingredients = input("Enter ingredients (comma-separated): ")
		recipes = bot.get_recipes_by_ingredients(ingredients)
		if recipes:
			for recipe in recipes:
				print(f"\nRecipe: {recipe['title']}")
				 
	elif choice == '2':
		diet = input("Enter dietary restriction (e.g., vegetarian, keto): ")
		exclude = input("Enter allergens to exclude: ")
		time = input("Enter maximum preparation time (minutes): ")
		recipes = bot.get_recipes_by_diet(diet, exclude, time)
		if recipes:
			for recipe in recipes:
				print(f"\nRecipe: {recipe['title']}")
				 
	elif choice == '3':
		recipe_id = input("Enter recipe ID: ")
		nutrition = bot.get_recipe_nutrition(recipe_id)
		if nutrition:
			bot.visualize_nutrition(nutrition)
			 
	elif choice == '4':
		recipe_id = input("Enter recipe ID: ")
		instructions = bot.get_recipe_instructions(recipe_id)
		if instructions:
			for step in instructions[0]['steps']:
				print(f"\nStep {step['number']}: {step['step']}")
				 
	elif choice == '5':
		 break

if __name__ == "__main__":
 main()

#works!