def classify_query(classifier, labels, query):
    result = classifier(query, candidate_labels=labels)
    return {
        "query": query,
        "top_label": result["labels"][0],
        "scores": dict(zip(result["labels"], result["scores"]))
    }