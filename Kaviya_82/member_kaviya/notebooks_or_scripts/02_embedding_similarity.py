# ============================================================
# EMBEDDING SIMILARITY FOR DRUG ANALOG SELECTION
# ============================================================

# Install required libraries first:
# pip install sentence-transformers scikit-learn

import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# 1. LOAD DATA
# ============================================================

with open("analog_drugs.json", "r") as f:
    analog_drugs = json.load(f)

with open("new_drug.json", "r") as f:
    new_drug = json.load(f)


print("Analog drugs loaded:", len(analog_drugs))
print("New drug:", new_drug["drug_name"])


# ============================================================
# 2. CREATE TEXT REPRESENTATION
# ============================================================

def create_embedding_text(drug):

    text = f"""
    Drug name: {drug['drug_name']}.
    Mechanism of action: {drug['mechanism_of_action']}.
    Route of administration: {drug['route_of_administration']}.
    Target specialty: {drug['target_specialty']}.
    Market size: {drug['market_size']}.
    Competitive density: {drug['competitive_density']}.
    Payer restrictiveness: {drug['payer_restrictiveness']}.
    Launch quarter: {drug['launch_quarter']}.
    Promotional intensity: {drug['promotional_intensity']}.
    Special designation: {drug['special_designation']}.
    Price tier: {drug['price_tier']}.
    """

    # Remove unnecessary spaces and new lines
    return " ".join(text.split())


# Create text for every analog drug
analog_texts = []

for drug in analog_drugs:
    text = create_embedding_text(drug)
    analog_texts.append(text)


# Create text for the new drug
new_drug_text = create_embedding_text(new_drug)


# ============================================================
# 3. LOAD EMBEDDING MODEL
# ============================================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# 4. GENERATE EMBEDDINGS
# ============================================================

analog_embeddings = model.encode(
    analog_texts,
    convert_to_numpy=True
)

new_drug_embedding = model.encode(
    [new_drug_text],
    convert_to_numpy=True
)


print("\nEmbedding generation completed.")

print(
    "Analog embedding shape:",
    analog_embeddings.shape
)

print(
    "New drug embedding shape:",
    new_drug_embedding.shape
)


# ============================================================
# 5. CALCULATE COSINE SIMILARITY
# ============================================================

similarity_scores = cosine_similarity(
    new_drug_embedding,
    analog_embeddings
)[0]


# ============================================================
# 6. ADD SIMILARITY SCORE TO EACH DRUG
# ============================================================

for drug, score in zip(
    analog_drugs,
    similarity_scores
):

    drug["embedding_similarity"] = float(score)


# ============================================================
# 7. RANK ANALOG DRUGS
# ============================================================

ranked_drugs = sorted(
    analog_drugs,
    key=lambda x: x["embedding_similarity"],
    reverse=True
)


# ============================================================
# 8. DISPLAY TOP 10 ANALOG DRUGS
# ============================================================

print("\n==========================================")
print("TOP 10 MOST SIMILAR ANALOG DRUGS")
print("==========================================")

for rank, drug in enumerate(
    ranked_drugs[:10],
    start=1
):

    print(
        f"{rank}. "
        f"{drug['drug_id']} - "
        f"{drug['drug_name']} "
        f"| Similarity: "
        f"{drug['embedding_similarity']:.4f}"
    )


# ============================================================
# 9. SAVE RESULTS
# ============================================================

with open(
    "ranked_analog_drugs.json",
    "w"
) as f:

    json.dump(
        ranked_drugs,
        f,
        indent=2
    )


print(
    "\nResults saved to "
    "'ranked_analog_drugs.json'"
)