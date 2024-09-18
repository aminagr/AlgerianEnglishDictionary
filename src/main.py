import json
import os
import re
from fuzzywuzzy import process


# Function to load JSON data from file
def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)


# Function to create reverse dictionary
def create_reverse_dictionary(data):
    reverse_data = {}
    for key, value in data.items():
        if isinstance(value, list):  # Handle cases where translations are lists
            for item in value:
                for translation in item['translations']:
                    reverse_data[normalize_text(translation)] = (key, item['example'])
        else:
            for translation in value['translations']:
                reverse_data[normalize_text(translation)] = (key, value['example'])
    return reverse_data


# Function to normalize text
def normalize_text(text):
    return re.sub(r'\W+', '', text.lower())


# Function to suggest words with improved relevance
def suggest_word(word, reverse_data):
    normalized_word = normalize_text(word)

    # Attempt to find the closest match in the reverse dictionary
    choices = list(reverse_data.keys())

    # Filter out suggestions that don't start with the same prefix
    filtered_choices = [choice for choice in choices if choice.startswith(normalized_word[0])]

    if filtered_choices:
        best_match, score = process.extractOne(normalized_word, filtered_choices)
    else:
        best_match, score = process.extractOne(normalized_word, choices)

    if score > 80:  # Threshold for considering a match
        return best_match, reverse_data[best_match]
    else:
        return None, None


# Function to look up translations
def lookup(word, data):
    normalized_word = normalize_text(word)

    if normalized_word in data:
        entry = data[normalized_word]
        if isinstance(entry, list):
            for idx, item in enumerate(entry):
                print(
                    f"{idx + 1}- '{word}' in Algerian is '{item['translations'][0]}'. "
                    f"Example: '{item['example']['arabic']}' means '{item['example']['english']}'"
                )
        else:
            print(
                f"'{word}' means '{entry['translations'][0]}' in Algerian. "
                f"Example: '{entry['example']['arabic']}' means '{entry['example']['english']}'"
            )
        return True
    return False


# Function to handle translation lookup and suggestions
def translate(word, data, reverse_data):
    if lookup(word, data):
        return

    # If not found, provide suggestions with improved relevance
    suggestion, details = suggest_word(word, reverse_data)

    if suggestion:
        english_word, example = details
        print(
            f"'{word}' not found in the dictionary. Maybe you mean '{suggestion}' "
            f"which means '{english_word}' in English. "
            f"Example: '{example['arabic']}' means '{example['english']}'"
        )
    else:
        print("Word not found in the dictionary and no suggestions available.")


# Main function
def main():
    # Define the path to the JSON file relative to the script
    script_dir = os.path.dirname(__file__)
    filepath = os.path.join(script_dir, '../data/dictionnary.json')

    # Load data from JSON file
    data = load_data(filepath)

    # Create reverse dictionary
    reverse_data = create_reverse_dictionary(data)

    while True:
        user_input = input("Enter a word in English or Algerian Arabic (or 'exit' to quit): ").strip()
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        translate(user_input, data, reverse_data)


if __name__ == "__main__":
    main()
