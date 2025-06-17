import sqlite3
import streamlit as st
from hybrid_search import hybrid_search

# ─── Streamlit setup ────────────────────────────────────────────────────────
st.set_page_config(page_title="🍽️ Recipe Chatbot", layout="wide")
st.markdown(
    f"""
    <style>
      /* full‐page background with a black fade overlay */
      .stApp {{
        background: 
          linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)),
          url("https://towardsdatascience.com/wp-content/uploads/2021/07/0wsWIB7I_n0XYMGca-scaled.jpg");
        background-size: cover;
        background-position: center;
      }}
      /* make sure the main container stays transparent */
      .block-container {{
        background: none;
      }}
      /* keep all text left-aligned as before */
      h1, p {{ text-align: left !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)
   

st.title("🍽️ Recipe Recommendation Chatbot")
st.write("Hey fellow hungry person, what would you like to eat today?")

user_input = st.text_input("Enter your preference:", key="query")

col1, col2 = st.columns(2)
with col1:
    if st.button("🔍 Search Recipes"):
        if not user_input:
            st.warning("Please enter something first!")
        else:
            recs = hybrid_search(user_input, top_k=10, vector_candidate_k=30)
            if not recs:
                st.info("No recipes found.")
            else:
                st.subheader("Here are recommendations for you:")
                for r in recs:
                    with st.expander(f"{r['title']} ({r['cuisine']} / {r['flavour_profile']})"):
                        # Uvijek ispiši prep_minutes
                        st.write(
                            f"- Servings: {r['servings']}, "
                            f"Prep time: {r['prep_minutes']} min, "
                            f"Rating: {r['rating']}"
                        )

                        conn = sqlite3.connect("recipes.db"); cur = conn.cursor()
                        cur.execute(
                            "SELECT ingredient FROM ingredients WHERE recipe_id = ?",
                            (r["id"],)
                        )
                        ingredients = [row[0] for row in cur.fetchall()]

                        cur.execute(
                            "SELECT directions FROM recipes WHERE id = ?",
                            (r["id"],)
                        )
                        dirs_row = cur.fetchone()
                        conn.close()

                        st.markdown("**Ingredients:**")
                        for item in ingredients:
                            st.markdown(f"- {item}")

                        st.markdown("**Directions:**")
                        st.write(dirs_row[0] if dirs_row else "")

with col2:
    if st.button("🤤 I'm Feeling Extra Hungry"):
        if not user_input:
            st.warning("Please enter something first!")
        else:
            recs = hybrid_search(user_input, top_k=1, vector_candidate_k=30)
            if not recs:
                st.info("No recipes found.")
            else:
                r = recs[0]
                st.subheader("Here's one for you:")
                st.write(
                    f"**{r['title']}** ({r['cuisine']} / {r['flavour_profile']})"
                )
                st.write(
                    f"- Servings: {r['servings']}, "
                    f"Prep time: {r['prep_minutes']} min, "
                    f"Rating: {r['rating']}"
                )

                conn = sqlite3.connect("recipes.db"); cur = conn.cursor()
                cur.execute(
                    "SELECT ingredient FROM ingredients WHERE recipe_id = ?",
                    (r["id"],)
                )
                ingredients = [row[0] for row in cur.fetchall()]

                cur.execute(
                    "SELECT directions FROM recipes WHERE id = ?",
                    (r["id"],)
                )
                dirs_row = cur.fetchone()
                conn.close()

                st.markdown("**Ingredients:**")
                for item in ingredients:
                    st.markdown(f"- {item}")

                st.markdown("**Directions:**")
                st.write(dirs_row[0] if dirs_row else "")
