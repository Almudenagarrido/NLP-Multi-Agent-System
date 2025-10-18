from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import json
import os
import random

TOPICS = ["finance"]
TRAIN_FILE = "data/examples.json"    
BASE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  
BATCH_SIZE = 16
EPOCHS = 3
LR = 2e-5
SEED = 42


for topic in TOPICS:
    random.seed(SEED)
    SAVE_DIR = f"{topic}-embed-model"
    def load_examples(jsonl_path):
        examples = []
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                obj = json.loads(line)
                q = obj.get("query")
                pos = obj.get("positive")
                if q and pos:
                    examples.append(InputExample(texts=[q, pos]))
        return examples

    train_examples = load_examples(TRAIN_FILE)
    print(f"Loaded {len(train_examples)} training examples.")
    model = SentenceTransformer(BASE_MODEL)
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=BATCH_SIZE)
    train_loss = losses.MultipleNegativesRankingLoss(model)
    warmup_steps = int(len(train_dataloader) * EPOCHS * 0.1)
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=EPOCHS,
        warmup_steps=warmup_steps,
        optimizer_params={'lr': LR},
        output_path=SAVE_DIR
    )

    print(f"Training complete! Model saved to '{SAVE_DIR}'")
