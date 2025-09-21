
import streamlit as st
import numpy as np
from utils import load_model, load_corpus, precompute_embeddings, cosine_topk

st.title("🔎 Find similar movies by description")
st.caption("Powered by a SentenceTransformer embedding model and cosine similarity.")

films = load_corpus()
with st.spinner("Preparing embeddings (cached after first run)..."):
    emb_matrix = precompute_embeddings(films["description"].tolist())

user_text = st.text_area(
    "Describe a movie you have in mind (plot, themes, vibes)…",
    height=140,
    placeholder="e.g., A retired hitman seeks revenge after his dog is killed, leading to stylish action set pieces",
)

if st.button("Get Your Prediction", type="primary"):
    if not user_text.strip():
        st.warning("Please enter a description first.")
    else:
        model = load_model()
        q = model.encode([user_text], normalize_embeddings=True, show_progress_bar=False)[0]

        # cosine scores since embeddings are normalized
        sims = emb_matrix @ q                      # shape: (num_films,)

        idxs = cosine_topk(q, emb_matrix, k=3)     # keep your existing top-k
        st.subheader("Top matches")
        for rank, idx in enumerate(idxs, start=1):
            row = films.iloc[idx]
            score = float(sims[idx])               # in [-1, 1]
            with st.container(border=True):
                st.markdown(f"**#{rank} — {row['title']}**")
                st.markdown(f"MATCH: `{score*100:.1f}%`")
                st.markdown(f"Rating: `{row['rating']}`")
                with st.expander("Show description"):
                    st.write(row["description"])
        # after you compute q
        # sims = emb_matrix @ q  # cosine scores in [-1, 1]
        # k = 3
        # topk = np.argpartition(-sims, k)[:k]
        # topk = topk[np.argsort(-sims[topk])]

        # st.subheader("Top matches")
        # for rank, idx in enumerate(topk, 1):
        #     row = films.iloc[idx]
        #     score = float(sims[idx])
        #     pct = score * 100.0

        #     with st.container(border=True):
        #         st.markdown(f"**#{rank} — {row['title']}**")

        #         # two neat bits: a metric and a tiny progress bar
        #         c1, c2 = st.columns([1, 1])
        #         with c1:
        #             st.metric("MATCH", f"{pct:.1f}%")     # big, readable number
        #         with c2:
        #             st.markdown(f"**Rating**\n\n`{row['rating']}`")

        #         # Map cosine [-1,1] -> [0,1] for the progress bar (clamped for safety)
        #         bar_val = max(0.0, min(1.0, (score + 1.0) / 2.0))
        #         st.progress(bar_val, text=f"Similarity meter")

        #         with st.expander("Show description"):
        #             st.write(row["description"])
