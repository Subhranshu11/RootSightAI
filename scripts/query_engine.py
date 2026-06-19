import os
import pickle
import faiss
import numpy as np
import uuid

from datetime import datetime

import streamlit as st

from groq import Groq
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

DYNAMIC_FAISS_PATH = "dynamic_vectorstore/dynamic_faiss.bin"
DYNAMIC_METADATA_PATH = "dynamic_vectorstore/dynamic_metadata.pkl"
def load_dynamic_repository():

    if (
        os.path.exists(DYNAMIC_FAISS_PATH)
        and
        os.path.exists(DYNAMIC_METADATA_PATH)
    ):

        dynamic_index = faiss.read_index(
            DYNAMIC_FAISS_PATH
        )

        with open(
            DYNAMIC_METADATA_PATH,
            "rb"
        ) as f:

            dynamic_metadata = pickle.load(f)

        return dynamic_index, dynamic_metadata

    return None, []
# -----------------------------------
# VALID ENTERPRISE KEYWORDS
# -----------------------------------

VALID_ENTERPRISE_KEYWORDS = [
    "incident",
    "scheduler",
    "deployment",
    "etl",
    "dashboard",
    "report",
    "failure",
    "job",
    "refresh",
    "service",
    "server",
    "rca",
    "workflow",
    "database",
    "latency",
    "timeout",
    "ticket",
    "pipeline",
    "application",
    "analytics",
    "data",
    "monitoring",
    "batch",
    "refresh failure",
    "operational",
    "production",
    "alert"
]

# -----------------------------------
# ENTERPRISE QUERY VALIDATION
# -----------------------------------

def is_enterprise_query(user_query):

    user_query = user_query.lower()

    for keyword in VALID_ENTERPRISE_KEYWORDS:

        if keyword in user_query:
            return True

    return False

# -----------------------------------
# LOAD ENV VARIABLES
# -----------------------------------

load_dotenv()

try:

    # Streamlit Cloud
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

except:

    # Local Development
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# -----------------------------------
# PATHS
# -----------------------------------

FAISS_INDEX_PATH = "vectorstore/faiss_index.bin"
METADATA_PATH = "vectorstore/metadata.pkl"

# -----------------------------------
# LOAD EMBEDDING MODEL
# -----------------------------------

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# -----------------------------------
# LOAD FAISS INDEX
# -----------------------------------

print("Loading FAISS index...")

index = faiss.read_index(
    FAISS_INDEX_PATH
)

# -----------------------------------
# LOAD METADATA
# -----------------------------------

print("Loading metadata...")

with open(METADATA_PATH, "rb") as f:

    metadata = pickle.load(f)

# -----------------------------------
# LOAD GROQ CLIENT
# -----------------------------------

client = Groq(
    api_key=GROQ_API_KEY
)

# -----------------------------------
# MAIN INCIDENT ANALYSIS FUNCTION
# -----------------------------------

def keyword_search(query, metadata, top_n=2):

    query = query.lower()

    keyword_results = []

    for chunk in metadata:

        score = 0

        chunk_lower = chunk.lower()

        for word in set(query.split()):

            if word in chunk_lower:
                score += 1

        if score > 0:

            keyword_results.append(
                (score, chunk)
            )

    keyword_results.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    return [
        chunk
        for score, chunk
        in keyword_results[:top_n]
    ]

def analyze_incident(
    user_query,
    return_context=False
):
    dynamic_index, dynamic_metadata = (
        load_dynamic_repository()
    )
    USE_DYNAMIC_REPOSITORY = (
        dynamic_index is not None
        and
        len(dynamic_metadata) > 0
    )
    if dynamic_metadata is None:
        dynamic_metadata = []

    # -----------------------------------
    # STEP 1 — CREATE QUERY EMBEDDING
    # -----------------------------------

    query_embedding = embedding_model.encode(
        [user_query]
    )

    query_embedding = np.array(
        query_embedding
    ).astype("float32")

    print("Metadata Size:", len(metadata))
    # -----------------------------------
    # STEP 2 — SEARCH FAISS
    # -----------------------------------

    top_k = 1

    all_chunks = []

    RELEVANCE_THRESHOLD = 1.125
    
    if USE_DYNAMIC_REPOSITORY:

        print("Using Dynamic Repository")

        distances, indices = (
            dynamic_index.search(
                query_embedding,
                top_k
            )
        )

        active_metadata = dynamic_metadata

    else:

        print("Using Static Repository")

        distances, indices = (
            index.search(
                query_embedding,
                top_k
            )
        )

        active_metadata = metadata

    retrieved_scores = []

    for distance, idx in zip(
        distances[0],
        indices[0]
    ):
    
        if (
            idx < len(active_metadata)
            and
            distance <= RELEVANCE_THRESHOLD
        ):
    
            all_chunks.append(
                active_metadata[idx]
            )
    
            retrieved_scores.append(
                float(distance)
            )
    
            retrieved_scores.append(
                float(distance)
            )
    if not retrieved_scores:

        scope_message = """
    ## Scope Restriction Notice
    
    No relevant enterprise operational knowledge was found.
    
    Query is outside the operational knowledge base scope.
    """
    
        if return_context:
    
            return {
                "response": scope_message,
                "context": [],
                "knowledge_source": "Out Of Scope"
            }
    
        return scope_message
    best_score = min(retrieved_scores)
    similar_chunks = 0

    for score in retrieved_scores:
    
        if score <= 1.125:
            similar_chunks += 1
    
    print(f"Highly Similar Chunks: {similar_chunks}")
    
    if USE_DYNAMIC_REPOSITORY:

        MIN_MATCHES = 1
    
    else:
    
        MIN_MATCHES = 1
    if (
        best_score > RELEVANCE_THRESHOLD
        or
        similar_chunks < MIN_MATCHES
    ):
    
        scope_message = """
    ## Scope Restriction Notice
    
    No relevant enterprise operational knowledge was found.
    
    Query is outside the operational knowledge base scope.
    """
    
        if return_context:
    
            return {
                "response": scope_message,
                "context": [],
                "knowledge_source": "Out Of Scope"
            }
    
        return scope_message
    # -----------------------------------
    # STEP 3 — RETRIEVE CONTEXT
    # -----------------------------------

    vector_chunks = list(
        dict.fromkeys(all_chunks)
    )
    
    combined_chunks = vector_chunks[:3]

    print(
        f"Retrieved {len(combined_chunks)} relevant chunks (max=3)"
    )

    # -----------------------------------
    # BUILD FINAL CONTEXT
    # -----------------------------------

    retrieved_context = ""

    for chunk in combined_chunks:

        retrieved_context += chunk
        retrieved_context += "\n\n----------------------\n\n"

    print(
        f"Vector Chunks: {len(vector_chunks)}"
    )

    print(
        f"Combined Chunks: {len(combined_chunks)}"
    )

    print(f"Final Context Size: {len(retrieved_context)} chars")

    print(
        f"Dynamic Chunks Loaded: {len(dynamic_metadata)}"
    )
    print(
        f"Total Retrieved Chunks: {len(all_chunks)}"
    )

    # -----------------------------------
    # STEP 4 — CREATE PROMPT
    # -----------------------------------
    knowledge_source = (
        "Uploaded Enterprise Documents"
        if USE_DYNAMIC_REPOSITORY
        else
        "Historical Knowledge Base"
    )
    prompt = f"""
You are an enterprise operational intelligence assistant specialized in reporting and analytics environments, enterprise-grade incident analysis.
You are an enterprise operational intelligence copilot.

IMPORTANT:

If retrieved context contains:
- Resolution Steps
- Solution
- Remediation Procedure
- Recovery Procedure

then reproduce those steps exactly.

Never invent operational procedures.

Never create new click-by-click instructions.

If no procedure exists in retrieved context,
state:

"No documented remediation procedure found in retrieved knowledge."

STRICT RULES:
- Do NOT generate generic AI explanations
- Do NOT speculate outside provided context
- Keep response concise and operational
- Focus only on enterprise reporting operations
- Avoid unnecessary technical jargon
- Keep each section short and actionable
- Use bullet points wherever appropriate
- If information is unavailable in enterprise context, clearly mention it
- Never answer outside enterprise operational scope
- Every RCA must be grounded in retrieved context
- Never generate remediation steps not present in context
- If evidence is insufficient, say so
- Do not assume missing operational details

Your role:
- Analyze operational incidents
- Predict probable root causes
- Identify affected systems
- Suggest remediation steps
- Correlate historical incidents
- Use the enterprise operational knowledge provided below

Enterprise Operational Knowledge Base:
{retrieved_context}

Knowledge Source:
{knowledge_source}

Current Incident:
{user_query}

Provide response EXACTLY in this format:

## Incident Summary
(2-3 concise lines)

## Probable Root Cause
- Point 1
- Point 2
- Point 3

## Affected Components
- Component 1
- Component 2

## Actionable Remediation

IMPORTANT:

If explicit resolution steps exist in the retrieved knowledge,
copy those steps exactly as written.

Do NOT rewrite.
Do NOT summarize.
Do NOT create new remediation steps.

Only generate remediation steps when no resolution procedure exists.

## Preventive Recommendation
- Recommendation 1
- Recommendation 2

## Operational Insight
(1 concise enterprise operational observation)
"""

    # -----------------------------------
    # STEP 5 — CALL GROQ
    # -----------------------------------

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
You are an enterprise operational intelligence copilot.

You ONLY answer enterprise operational incident queries.

Never behave like a generic chatbot.

Never provide unrelated information.

Keep all responses concise, enterprise-focused, and operationally scoped.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    # -----------------------------------
    # STEP 6 — RETURN RESPONSE
    # -----------------------------------

    final_response = response.choices[0].message.content

    if return_context:

        return {
            "response": final_response,
            "context": combined_chunks
        }

    return final_response

# -----------------------------------
# ADD NEW INCIDENT TO KNOWLEDGE BASE
# -----------------------------------

def add_incident_to_knowledgebase(
    user_query,
    ai_response
):

    # -----------------------------------
    # GENERATE INCIDENT ID
    # -----------------------------------

    incident_id = f"INC-{str(uuid.uuid4())[:8].upper()}"

    # -----------------------------------
    # TIMESTAMP
    # -----------------------------------

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # -----------------------------------
    # CREATE INCIDENT CHUNK
    # -----------------------------------

    new_chunk = f"""
INCIDENT ID: {incident_id}

TIMESTAMP: {timestamp}

NEW INCIDENT REPORTED

Incident Details:
{user_query}

AI RCA Analysis:
{ai_response}
"""

    # -----------------------------------
    # CREATE EMBEDDING
    # -----------------------------------

    new_embedding = embedding_model.encode(
        [new_chunk]
    )

    new_embedding = np.array(
        new_embedding
    ).astype("float32")

    # -----------------------------------
    # ADD TO FAISS INDEX
    # -----------------------------------

    index.add(new_embedding)

    # -----------------------------------
    # ADD TO METADATA
    # -----------------------------------

    metadata.append(new_chunk)

    # -----------------------------------
    # SAVE UPDATED FAISS INDEX
    # -----------------------------------

    faiss.write_index(
        index,
        FAISS_INDEX_PATH
    )

    # -----------------------------------
    # SAVE UPDATED METADATA
    # -----------------------------------

    with open(METADATA_PATH, "wb") as f:

        pickle.dump(metadata, f)

    print(f"New incident stored: {incident_id}")

    return incident_id
