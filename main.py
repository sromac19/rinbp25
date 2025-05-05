from sqlite_setup import setup_sqlite
from weaviate_setup import setup_weaviate
from recommend import recommend_by_ingredient_flavor

if __name__ == "__main__":
    print("📦 Postavljanje SQLite baze...")
    setup_sqlite()
    print("🔍 Postavljanje Weaviatea...")
    setup_weaviate()
    print("🤖 Preporučeni recepti za: 'creamy savory bacon'")
    recommend_by_ingredient_flavor("creamy savory bacon")
