from sqlite_setup import initialize_sqlite_db
from weaviate_setup import initialize_weaviate_schema
from recommend import recommend_recipes

def main():
    initialize_sqlite_db()
    initialize_weaviate_schema()

    query = "creamy savory bacon"
    recommendations = recommend_recipes(query)

    print(f"Recommendations for query: '{query}'\n")
    for recipe in recommendations:
        print(f"Recipe: {recipe['name']}")
        print(f"Ingredients: {recipe['ingredients']}")
        print(f"Flavor profile: {recipe['flavor_profile']}\n")

if __name__ == "__main__":
    main()
