import sqlite3
import streamlit as st
from hybrid_search import hybrid_search

# ─── Streamlit setup ────────────────────────────────────────────────────────
st.set_page_config(page_title="🍽️ Recipe Chatbot", layout="wide")
st.markdown("""
  <style>
    .block-container { max-width: 900px; padding: 1rem 2rem; }
    h1, p { text-align: left !important; }
  </style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
      /* 1) Fade background image */
      [data-testid="stAppViewContainer"] {
        position: relative;
        z-index: 0;
      }
      [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top:0; left:0; right:0; bottom:0;
        background: url('https://towardsdatascience.com/wp-content/uploads/2021/07/0wsWIB7I_n0XYMGca-scaled.jpg') center/cover no-repeat;
        filter: brightness(0.15) contrast(1.1);
        z-index: -1;
        pointer-events: none;
      }

      /* 2) Main container styling */
      .block-container {
        background-color: rgba(0,0,0,0.7) !important;
        padding: 1rem 2rem;
        border-radius: 12px;
      }

      /* 3) Text & headers white */
      .block-container h1,
      .block-container h2,
      .block-container h3,
      .block-container p,
      .block-container .stText {
        color: #FFFFFF !important;
      }

      /* 4) Input box styling */
      .stTextInput>div>div>input {
        background-color: #333 !important;
        color: #fff !important;
        border: 1px solid #555 !important;
      }
      .stTextInput>div>div>input::placeholder {
        color: #bbb !important;
      }

      /* 5) Primary button */
      button[kind="primary"] {
        background-color: #e63946 !important;
        color: #fff !important;
        border-radius: 8px !important;
      }
      /* 6) Secondary button */
      button[kind="secondary"] {
        background-color: #f1c40f !important;
        color: #000 !important;
        border-radius: 8px !important;
      }

      /* 7) Expander headers */
      .stExpanderHeader {
        background-color: rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        color: #fff !important;
      }
    </style>
    """,
    unsafe_allow_html=True
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

