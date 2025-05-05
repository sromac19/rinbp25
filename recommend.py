import weaviate

def recommend_recipes(query: str, top_k=5):
    client = weaviate.Client("http://localhost:8080")

    result = client.query.get("Recipe", ["name", "ingredients", "flavor_profile"])\
        .with_near_text({"concepts": [query]})\
        .with_limit(top_k)\
        .do()

    return result["data"]["Get"]["Recipe"]
