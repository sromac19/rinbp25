import weaviate
import json

def setup_weaviate():
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

    with open("data/recipes.json", "r") as f:
        data = json.load(f)

    for recipe in data:
        client.data_object.create(
            data_object={
                "name": recipe["name"],
                "ingredients": ", ".join(recipe["ingredients"]),
                "flavor_profile": recipe["flavor_profile"]
            },
            class_name="Recipe"
        )

if __name__ == "__main__":
    setup_weaviate()
