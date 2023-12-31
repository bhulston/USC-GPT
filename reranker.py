from sentence_transformers import CrossEncoder
import numpy as np

# Let's use a reranker to get better results from our semantic search

def reranker(query, matches):

    pairs = []
    
    for match in matches:
        pairs.append([query, match["metadata"]["text"]])
    
    model = CrossEncoder('cross-encoder/ms-marco-TinyBERT-L-2-v2', max_length = 512)

    scores = model.predict(pairs)
    top_indices = np.argsort(scores)[::-4]
    top_results = ["Class: " + matches[index]["metadata"]["text"] + "Class Url: " + matches[index]["metadata"]["url"] + "Class Time: " + str(matches[index]["metadata"]["time"]) for index in top_indices]
    return top_results