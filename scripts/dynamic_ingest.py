import os
import pickle
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer

DYNAMIC_FOLDER = "dynamic_workspace"

VECTORSTORE_FOLDER = "dynamic_vectorstore"

FAISS_PATH = os.path.join(
    VECTORSTORE_FOLDER,
    "dynamic_faiss.bin"
)

METADATA_PATH = os.path.join(
    VECTORSTORE_FOLDER,
    "dynamic_metadata.pkl"
)

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

import pandas as pd
import json

def read_file(file_path):

    ext = os.path.splitext(file_path)[1].lower()

    try:

        # TXT / LOG / MD / XML
        if ext in [".txt", ".log", ".md", ".xml"]:

            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                return f.read()

        # CSV
        elif ext == ".csv":

            df = pd.read_csv(
                file_path
            )

            return df.to_string(
                index=False
            )

        # XLSX
        elif ext == ".xlsx":

            df = pd.read_excel(
                file_path
            )

            return df.to_string(
                index=False
            )

        # JSON
        elif ext == ".json":

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            return json.dumps(
                data,
                indent=2
            )

    except Exception as e:

        print(
            f"READ ERROR: {file_path}"
        )

        print(e)

        return ""

    return ""

def build_dynamic_repository():

    os.makedirs(
        VECTORSTORE_FOLDER,
        exist_ok=True
    )

    chunks = []

    for filename in os.listdir(DYNAMIC_FOLDER):

        file_path = os.path.join(
            DYNAMIC_FOLDER,
            filename
        )

        content = read_file(file_path)

        if not content:
            continue

        for i in range(
            0,
            len(content),
            1000
        ):

            chunks.append(
                f"FILE: {filename}\n\n{content[i:i+1000]}"
            )

    if not chunks:
        return False

    embeddings = embedding_model.encode(
        chunks
    )

    embeddings = np.array(
        embeddings
    ).astype("float32")

    index = faiss.IndexFlatL2(
        embeddings.shape[1]
    )

    index.add(
        embeddings
    )

    faiss.write_index(
        index,
        FAISS_PATH
    )

    with open(
        METADATA_PATH,
        "wb"
    ) as f:

        pickle.dump(
            chunks,
            f
        )
    return True