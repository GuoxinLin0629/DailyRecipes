from flask import Flask, request, jsonify, render_template
from recipe_bot import RecipeBot
import json

app = Flask(__name__)
bot = RecipeBot()

@app.route('/')
def home():
    
    return render_template('index.html')

@app.route('/get_recipe', methods=['POST'])
def get_recipe():
    
    try:
        user_input = request.json.get('query')
        if not user_input:
            return jsonify({"error": "No query provided"}), 400

        response = bot.client.chat.completions.create(
            model="GPT-4",
            messages=[
                {"role": "system", "content": "Extract recipe search parameters from user input."},
                {"role": "user", "content": user_input}
            ],
            tools=bot.functions,
            tool_choice="auto"
        )

        if response.choices[0].message.tool_calls:
            args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
            recipes = bot.get_recipe(
                args.get('ingredients'),
                args.get('diet'),
                args.get('maxTime')
            )
            if recipes:
                
                recipe_data = []
                for recipe in recipes:
                    recipe_info = {
                        'title': recipe['title'],
                        'id': recipe['id'],
                        'readyMinutes': recipe.get('readyMinutes'),
                        'image': recipe.get('image'),
                        'ingredients': recipe.get('ingredients', []),
                        'instructions': recipe.get('instructions', []),
                        'video': recipe.get('video'),
                        'nutrition': recipe.get('nutrition')
                    }
                    recipe_data.append(recipe_info)
                return jsonify({"success": True, "recipes": recipe_data})
            return jsonify({"success": False, "message": "No recipes found."})
        return jsonify({"success": False, "message": "Could not understand request."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
