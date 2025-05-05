import weaviate
import json

def initialize_weaviate_schema():
    client = weaviate.Client("http://localhost:8080")

    if client.schema.contains({"class": "Recipe"}):
        client.schema.delete_class("Recipe")

    schema = {
        "class": "Recipe",
        "vectorizer": "text2vec-openai",
        "properties": [
            {"name": "name", "dataType": ["text"]},
            {"name": "ingredients", "dataType": ["text"]},
            {"name": "flavor_profile", "dataType": ["text"]}
        ]
    }

    client.schema.create_class(schema)

    with open("data/recipes.json", "r") as file:
        recipes = json.load(file)

    for recipe in recipes:
        client.data_object.create(
            data_object={
                "name": recipe["name"],
                "ingredients": ", ".join(recipe["ingredients"]),
                "flavor_profile": recipe["flavor_profile"]
            },
            class_name="Recipe"
        )

if __name__ == "__main__":
    initialize_weaviate_schema()
