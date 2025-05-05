import weaviate

def recommend_by_ingredient_flavor(query: str, top_k=3):
    client = weaviate.Client("http://localhost:8080")
    result = client.query.get("Recipe", ["name", "ingredients", "flavor_profile"])\
        .with_near_text({"concepts": [query]})\
        .with_limit(top_k)\
        .do()

    for r in result["data"]["Get"]["Recipe"]:
        print("🍽️", r["name"])
        print("  🧂 Ingredients:", r["ingredients"])
        print("  🌶️ Flavor:", r["flavor_profile"])
        print()

if __name__ == "__main__":
    recommend_by_ingredient_flavor("creamy savory bacon")
