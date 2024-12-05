from flask import Flask, render_template, request
from utils.spoonacular import get_recipes, get_recipe_details,generate_instructions, generate_image
import pandas as pd

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')


def fetch_recipes():
    ingredients = request.form['ingredients']
    recipes = get_recipes(ingredients)
    return render_template('index.html', recipes=recipes)


def recipe_details(id):
    details = get_recipe_details(id)
    instructions = generate_instructions(details)
    return render_template('index.html', details=details, instructions=instructions)

def nutritional_analysis(id):
    details = get_recipe_details(id)
    nutrients = pd.DataFrame(details['nutrition'])
    # Example Pandas processing
    nutrients['Percent Daily Value'] = (nutrients['amount'] / nutrients['dailyValue']) * 100
    return render_template('index.html', nutrients=nutrients.to_dict())
