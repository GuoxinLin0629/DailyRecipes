from openai import AzureOpenAI
import os
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt

class RecipeBot:
    def __init__(self):
        try:
            print("Initializing Recipe Bot...")
            self.client = AzureOpenAI(
                api_key=os.getenv("AZURE_KEY"),
                azure_endpoint=os.getenv("AZURE_ENDPOINT"), 
                api_version="2023-12-01-preview"
            )
            self.api_key = self.load_api_key()
            self.functions = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_recipe",
                        "description": "Gets recipes based on ingredients",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "ingredients": {
                                    "type": "string",
                                    "description": "Comma-separated list of ingredients"
                                },
                                "diet": {
                                    "type": "string",
                                    "description": "Dietary restriction (e.g., vegetarian, keto)",
                                    "nullable": True
                                },
                                "maxTime": {
                                    "type": "integer",
                                    "description": "Maximum preparation time in minutes",
                                    "nullable": True
                                }
                            },
                            "required": ["ingredients"]
                        }
                    }
                }
            ]
            print("Initialization complete")
        except Exception as e:
            print(f"Error during initialization: {e}")
            raise

    def load_api_key(self):
        try:
            with open("spoonacularAPI_Key.txt", 'r') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error loading API key: {e}")
            raise

    def get_recipe(self, ingredients, diet=None, maxTime=None):
        params = {
            "query": ingredients,
            "diet": diet,
            "maxReadyTime": maxTime,
            "number": 3, 
            "addRecipeInformation": True,
            "fillIngredients": True,
            "apiKey": self.api_key
        }

        params = {k: v for k, v in params.items() if v is not None}
        #print(f"Searching with parameters: {params}")

        try:
            response = requests.get(
                "https://api.spoonacular.com/recipes/complexSearch",
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    return self.process_recipes(data['results'])
            return None
        except Exception as e:
            print(f"Error in recipe search: {e}")
            return None

    def get_recipe_instructions(self, recipe_id):
        try:
            response = requests.get(
                f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions",
                params={"apiKey": self.api_key}
            )
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    return [step['step'] for step in data[0].get('steps', [])]
            return []
        except Exception as e:
            print(f"Error getting instructions: {e}")
            return []

    def get_nutrition(self, recipe_id):
        try:
            response = requests.get(
                f"https://api.spoonacular.com/recipes/{recipe_id}/nutritionWidget.json",
                params={"apiKey": self.api_key}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting nutrition info: {e}")
            return None

    def generate_recipe_image(self, recipe_name):
        try:
            print(f"Generating image for {recipe_name}...")
            response = self.client.images.generate(
                model="dalle3",
                prompt=f"A professional food photography of {recipe_name}, on a beautiful plate, restaurant style",
                n=1,
                size="1024x1024"
            )
            return response.data[0].url
        except Exception as e:
            print(f"Error generating image: {e}")
            return None

    def get_recipe_video(self, recipe_name):
        try:
            response = requests.get(
                "https://api.spoonacular.com/food/videos/search",
                params={
                    "query": recipe_name,
                    "number": 1,
                    "apiKey": self.api_key
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('videos'):
                    return f"https://www.youtube.com/watch?v={data['videos'][0]['youTubeId']}"
            return None
        except Exception as e:
            print(f"Error getting video link: {e}")
            return None

    def visualize_nutrition(self, nutrition_data):
        try:
            nutrients = {
                'Nutrient': ['Calories', 'Protein', 'Fat', 'Carbs'],
                'Amount': [
                    float(nutrition_data.get('calories', '0').rstrip(' kcal')),
                    float(nutrition_data.get('protein', '0').rstrip('g')),
                    float(nutrition_data.get('fat', '0').rstrip('g')),
                    float(nutrition_data.get('carbs', '0').rstrip('g'))
                ]
            }

            df = pd.DataFrame(nutrients)

            # 
            plt.figure(figsize=(10, 6))
            bars = plt.bar(df['Nutrient'], df['Amount'])
            plt.title('Nutritional Information')
            plt.ylabel('Amount')

            # 
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}',
                        ha='center', va='bottom')

            plt.xticks(rotation=45)
            plt.tight_layout()

            #
            print("\nNutritional Information:")
            print(df.to_string(index=False))
            plt.show()

            return df
        except Exception as e:
            print(f"Error visualizing nutrition: {e}")
            return None

    def process_recipes(self, recipes):
        detailed_recipes = []
        for recipe in recipes:
            try:
                recipe_details = {
                    'id': recipe['id'],
                    'title': recipe['title'],
                    'readyInMinutes': recipe.get('readyInMinutes'),
                    'ingredients': recipe.get('extendedIngredients', []),
                    'instructions': self.get_recipe_instructions(recipe['id']),
                    'nutrition': self.get_nutrition(recipe['id']),
                    'image': self.generate_recipe_image(recipe['title']),
                    'video': self.get_recipe_video(recipe['title'])
                }
                detailed_recipes.append(recipe_details)
            except Exception as e:
                print(f"Error processing recipe {recipe.get('title', 'unknown')}: {e}")
                continue
        return detailed_recipes

    def format_recipe_output(self, recipes):
        output = []
        for recipe in recipes:
            try:
                output.append("\n" + "="*50)
                output.append(f"Recipe: {recipe['title']}")
                output.append(f"Recipe ID: {recipe['id']}")

                if recipe.get('readyInMinutes'):
                    output.append(f"Preparation Time: {recipe['readyInMinutes']} minutes")

                if recipe.get('image'):
                    output.append(f"\nRecipe Image: {recipe['image']}")

                if recipe.get('ingredients'):
                    output.append("\nIngredients:")
                    for ing in recipe['ingredients']:
                        output.append(f"- {ing.get('amount', '')} {ing.get('unit', '')} {ing.get('name', '')}")

                if recipe.get('instructions'):
                    output.append("\nCooking Instructions:")
                    for i, step in enumerate(recipe['instructions'], 1):
                        output.append(f"Step {i}: {step}")

                    if recipe.get('video'):
                        output.append(f"\nCooking Tutorial Video: {recipe['video']}")

                if recipe.get('nutrition'):
                    self.visualize_nutrition(recipe['nutrition'])

                output.append("\n" + "="*50)
            except Exception as e:
                print(f"Error formatting recipe output: {e}")
                continue

        return "\n".join(output)

    def process_user_request(self, user_input):
        messages = [
            {"role": "system", "content": "Extract recipe search parameters from user input."},
            {"role": "user", "content": user_input}
        ]

        response = self.client.chat.completions.create(
            model="GPT-4",
            messages=messages,
            tools=self.functions,
            tool_choice="auto"
        )

        if response.choices[0].message.tool_calls:
            args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
            print(f"Parsed parameters: {args}")

            recipes = self.get_recipe(
                args.get('ingredients'),
                args.get('diet'),
                args.get('maxTime')
            )

            if recipes:
                return self.format_recipe_output(recipes)
            return f"No recipes found. Try different ingredients or criteria."

        return "I couldn't understand your request. Please try again."

def run_recipe_bot():
    bot = RecipeBot()
    print("\nWelcome to Recipe Bot!")
    print("You can:")
    print("1. Search recipes by ingredients")
    print("2. Specify dietary restrictions")
    print("3. Set maximum cooking time")
    #print("\nExample: 'Find me a recipe with chicken and rice that takes less than 30 minutes'")

    while True:
        user_input = input("\nWhat would you like to cook? (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
        response = bot.process_user_request(user_input)
        print(response)

if __name__ == "__main__":
    run_recipe_bot()
