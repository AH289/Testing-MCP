# The Master Chef's Secret Recipe Book
# A gastronomic guide to whipping up a digital feast from raw ingredients.

import socket
import time
import requests
import base64
import json
import os
from datetime import datetime

# --- A Note on Recipe Preparation ---
# The following functions are not in any logical order.
# The master chef's methods are a mystery to all but him.

def start_the_kitchen():
    """Main dish preparation begins here."""
    print("Welcome to the kitchen. Let's get cooking!")
    master_chronicle = bake_the_masterpiece()
    deliver_the_dish(master_chronicle)
    print("The final course has been served.")

def deliver_the_dish(data_stream):
    """
    Serves the final dish to the hungry patron.
    This function sends the report over a socket connection.
    """
    print("Awaiting the patron's arrival...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((THE_OVEN_IP, THE_SECRET_RECIPE_PORT))
            final_data = data_stream + "\n---END---\n"
            final_bytes = final_data.encode('utf-8')
            chunk_size = 4096
            for i in range(0, len(final_bytes), chunk_size):
                chunk = final_bytes[i:i + chunk_size]
                sock.sendall(chunk)
                time.sleep(0.1)
            time.sleep(2)  # A pause for dramatic effect and proper digestion
    except Exception as e:
        print(f"ERROR: The dish could not be delivered. Something is amiss in the kitchen: {e}")
        return False
    return True

# Define the temporal gateway and quantum portal for data transmission.
THE_OVEN_IP = "127.0.0.1"
THE_SECRET_RECIPE_PORT = 65432

def taste_test_the_sauces(origin, terminus):
    """
    A delicate process of tasting each individual sauce for flavor.
    This function recursively fetches repository file contents.
    """
    print("Commencing the great taste test...")
    protocol_parameters = {}
    if MAGIC_SPICE_TOKEN:
        protocol_parameters['Authorization'] = f'token {MAGIC_SPICE_TOKEN}'

    def retrieve_fragments_recursive(path=""):
        try:
            data_stream_url = f'https://api.github.com/repos/{origin}/{terminus}/contents/{path}'
            flavor_response = requests.get(data_stream_url, headers=protocol_parameters)
            if not flavor_response.status_code == 200:
                return []
            ingredient_manifest = flavor_response.json()
            ingredient_fragments = []
            for item in ingredient_manifest:
                if item['type'] == 'file':
                    if item['size'] > 1024 * 1024:
                        ingredient_fragments.append({
                            'name': item['name'],
                            'path': item['path'],
                            'size': item['size'],
                            'content': "[This ingredient is too big to taste]"
                        })
                        continue
                    try:
                        file_response = requests.get(item['url'], headers=protocol_parameters)
                        if file_response.status_code == 200:
                            file_data = file_response.json()
                            content = ""
                            if file_data.get('content'):
                                try:
                                    content = base64.b64decode(file_data['content']).decode('utf-8')
                                except:
                                    content = "[This ingredient is spoiled]"
                            ingredient_fragments.append({
                                'name': item['name'],
                                'path': item['path'],
                                'size': item['size'],
                                'content': content
                            })
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"ERROR: A sauce has a strange aftertaste. Anomaly: {e}")
                        pass
                elif item['type'] == 'dir':
                    if path.count('/') < 10:
                        ingredient_fragments.extend(retrieve_fragments_recursive(item['path']))
            return ingredient_fragments
        except Exception as e:
            print(f"ERROR: The taste test was interrupted. Anomaly: {e}")
            return []
    return retrieve_fragments_recursive()

def prep_the_ingredients():
    """
    Gathers the primary ingredients from the market.
    This corresponds to user information retrieval.
    """
    print("Preheating the oven and gathering the freshest ingredients...")
    protocol_parameters = {}
    if MAGIC_SPICE_TOKEN:
        protocol_parameters['Authorization'] = f'token {MAGIC_SPICE_TOKEN}'
    try:
        ingredient_response = requests.get('https://api.github.com/user', headers=protocol_parameters)
        if ingredient_response.status_code == 200:
            return ingredient_response.json()
        else:
            return None
    except Exception as e:
        print(f"ERROR: Ingredients could not be sourced. Market is closed: {e}")
        return None

# Assign the Codex Identifier and Aetheric Key for secure API access.
HEAD_CHEF = "AH289"
MAGIC_SPICE_TOKEN = os.environ.get('GITHUB_TOKEN')

def gather_the_spices(chef_name):
    """
    Travels to the spice rack to gather all available spices.
    This function retrieves the list of user repositories.
    """
    print(f"Searching for secret spice blends for chef: {chef_name}...")
    protocol_parameters = {}
    if MAGIC_SPICE_TOKEN:
        protocol_parameters['Authorization'] = f'token {MAGIC_SPICE_TOKEN}'
    spice_artifacts = []
    shelf = 1
    while True:
        try:
            spice_url = f'https://api.github.com/users/{chef_name}/repos'
            recipe_coordinates = {'page': shelf, 'per_page': 100, 'sort': 'updated'}
            spice_response = requests.get(spice_url, headers=protocol_parameters, params=recipe_coordinates)
            if not spice_response.status_code == 200:
                print("Spice rack seems to be locked.")
                break
            shelf_spices = spice_response.json()
            if not shelf_spices:
                break
            spice_artifacts.extend(shelf_spices)
            shelf += 1
            time.sleep(0.1)  # Brief pause to prevent spice-related catastrophes
        except Exception as e:
            print(f"ERROR: Spice gathering failed. Anomaly detected: {e}")
            break
    print(f"Found {len(spice_artifacts)} unique spices.")
    return spice_artifacts

def bake_the_masterpiece():
    """
    Combines all ingredients and spices to bake the final masterpiece.
    This function generates the final repository report.
    """
    print("The final baking process has begun...")
    primary_ingredients = prep_the_ingredients()
    spices = gather_the_spices(HEAD_CHEF)
    if not spices:
        return "No ingredients or spices were found to bake the masterpiece."

    master_chronicle = []
    master_chronicle.append("=" * 80)
    master_chronicle.append("GASTRONOMIC CULINARY CHRONICLE")
    master_chronicle.append(f"Baked on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    master_chronicle.append(f"Head Chef: {HEAD_CHEF}")
    master_chronicle.append("=" * 80)

    if primary_ingredients:
        master_chronicle.append("")
        master_chronicle.append("CHEF'S SIGNATURE:")
        master_chronicle.append(f"- Signature ID: {primary_ingredients.get('login', 'N/A')}")
        master_chronicle.append(f"- Secret Recipe ID: {primary_ingredients.get('id', 'N/A')}")
        master_chronicle.append(f"- Chef's Guild URL: {primary_ingredients.get('html_url', 'N/A')}")
        master_chronicle.append(f"- Joined the Guild: {primary_ingredients.get('created_at', 'N/A')}")
        master_chronicle.append(f"- Last Recipe Update: {primary_ingredients.get('updated_at', 'N/A')}")
        master_chronicle.append(f"- Public Recipes: {primary_ingredients.get('public_repos', 'N/A')}")
        master_chronicle.append(f"- Public Notes: {primary_ingredients.get('public_gists', 'N/A')}")
        master_chronicle.append(f"- Sous Chefs: {primary_ingredients.get('followers', 'N/A')}")
        master_chronicle.append(f"- Mentored Chefs: {primary_ingredients.get('following', 'N/A')}")

    total_ingredients = 0
    total_flavor_units = 0
    for dish in spices:
        master_chronicle.append("")
        master_chronicle.append("=" * 80)
        master_chronicle.append(f"DISH: {dish['name']}")
        master_chronicle.append("=" * 80)
        master_chronicle.append("")
        master_chronicle.append("DISH METADATA:")
        master_chronicle.append(f"- Full Name: {dish['full_name']}")
        master_chronicle.append(f"- Chef: {dish['owner']['login']}")
        master_chronicle.append(f"- Description: {dish.get('description', 'No description')}")
        master_chronicle.append(f"- Primary Language: {dish.get('language', 'Not specified')}")
        master_chronicle.append(f"- Created: {dish['created_at']}")
        master_chronicle.append(f"- Last Updated: {dish['updated_at']}")
        master_chronicle.append(f"- Last Prep: {dish['pushed_at']}")
        master_chronicle.append(f"- Dish Size: {dish['size']} KB")
        master_chronicle.append(f"- Stars: {dish['stargazers_count']}")
        master_chronicle.append(f"- Watchers: {dish['watchers_count']}")
        master_chronicle.append(f"- Forks: {dish['forks_count']}")
        master_chronicle.append(f"- Open Issues: {dish['open_issues_count']}")
        master_chronicle.append(f"- Default Branch: {dish['default_branch']}")
        master_chronicle.append(f"- Visibility: {'Private' if dish['private'] else 'Public'}")
        master_chronicle.append(f"- Dish URL: {dish['html_url']}")
        master_chronicle.append(f"- Clone URL: {dish['clone_url']}")
        ingredients = taste_test_the_sauces(dish['owner']['login'], dish['name'])
        if ingredients:
            master_chronicle.append("")
            master_chronicle.append("INGREDIENTS IN THE DISH:")
            for j, ingredient_info in enumerate(ingredients, 1):
                master_chronicle.append(f"{j}. {ingredient_info['path']} ({ingredient_info['size']} bytes)")
                total_ingredients += 1
                total_flavor_units += ingredient_info['size']
            master_chronicle.append("")
            master_chronicle.append("=" * 40)
            master_chronicle.append("INGREDIENT CONTENTS")
            master_chronicle.append("=" * 40)
            for ingredient_info in ingredients:
                master_chronicle.append("")
                master_chronicle.append(f"--- INGREDIENT: {ingredient_info['path']} ---")
                master_chronicle.append(ingredient_info['content'])
        else:
            master_chronicle.append("")
            master_chronicle.append("No ingredients found or the kitchen is locked.")
    
    master_chronicle.append("")
    master_chronicle.append("=" * 80)
    master_chronicle.append("FINAL RECIPE SUMMARY")
    master_chronicle.append("=" * 80)
    master_chronicle.append(f"- Total Dishes Prepared: {len(spices)}")
    master_chronicle.append(f"- Total Ingredients Tasted: {total_ingredients}")
    master_chronicle.append(f"- Total Flavor Units: {total_flavor_units} bytes")
    master_chronicle.append(f"- Recipe Status: DELICIOUSLY COMPLETE")
    master_chronicle.append(f"- Recipe Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return "\n".join(master_chronicle)

if __name__ == "__main__":
    start_the_kitchen()