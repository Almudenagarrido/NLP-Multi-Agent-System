import pandas as pd
import random
import re
import json

def create_jsons(input_path, output_path):
    df = pd.read_csv(input_path)
    df.to_json(output_path, orient='records', lines=False)

def create_examples(input_file, output_file, n_repetitions=1):
    with open(input_file, "r", encoding="utf-8") as f:
        articles = json.load(f)
    random.shuffle(articles)  
    out = []
    for _ in range(n_repetitions):
        for art in articles:
            title =art['title'].strip()
            title = re.sub(r"[\.\!\?]+$", "", title) # remove trailing punctuation
            patterns = [
                f"What happened regarding {title.lower()}?",
                f"Can you summarize: {title}?",
                f"Explain the news about {title.lower()}",
                f"Give me an update on {title.lower()}",
                f"Details on {title.lower()}?"
            ]
            query = random.choice(patterns)
            positive = art["summary"].strip()
            out.append({"query": query, "positive": positive})

    random.shuffle(articles)
    with open(output_file, "w", encoding="utf-8") as f:
        for ex in out:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    create_jsons("data/AAPL_news_20251017_204659.csv", "data/news.json")
    create_examples("data/news.json", "data/examples.json")

