from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Trainer, TrainingArguments
from datasets import Dataset

training_data = {
    "markets_trading": [
        {"input": "Passage: The S&P 500 surged by 1.2% today.\nQuestion: What happened to the S&P 500?\nAnswer:", 
         "output": "The S&P 500 increased by 1.2% today."},
        {"input": "Passage: Dow Jones fell 300 points amid tech sell-off.\nQuestion: How did the Dow Jones perform?\nAnswer:", 
         "output": "The Dow Jones dropped 300 points due to tech stock declines."},
        {"input": "Passage: Nasdaq closed at a record high this week.\nQuestion: How did Nasdaq close?\nAnswer:", 
         "output": "Nasdaq closed at a record high this week."},
        {"input": "Passage: Oil prices increased after OPEC announced production cuts.\nQuestion: What happened to oil prices?\nAnswer:", 
         "output": "Oil prices rose following OPEC's production cuts."},
        {"input": "Passage: Gold prices dipped slightly due to strong dollar.\nQuestion: How did gold perform?\nAnswer:", 
         "output": "Gold prices fell slightly as the dollar strengthened."}
    ],
    "corporate_business": [
        {"input": "Passage: Apple announced a new partnership with Ford.\nQuestion: What did Apple do?\nAnswer:", 
         "output": "Apple announced a partnership with Ford."},
        {"input": "Passage: Microsoft acquires a startup specializing in AI.\nQuestion: What acquisition did Microsoft make?\nAnswer:", 
         "output": "Microsoft acquired an AI-focused startup."},
        {"input": "Passage: Tesla opened a new factory in Germany.\nQuestion: What did Tesla do?\nAnswer:", 
         "output": "Tesla opened a new manufacturing plant in Germany."},
        {"input": "Passage: Amazon launches a new subscription service.\nQuestion: What did Amazon launch?\nAnswer:", 
         "output": "Amazon introduced a new subscription service."},
        {"input": "Passage: Google updates its privacy policy for cloud users.\nQuestion: What did Google update?\nAnswer:", 
         "output": "Google updated its cloud privacy policy."}
    ],
    "crypto_digital_assets": [
        {"input": "Passage: Bitcoin price surged 10% after major ETF approval.\nQuestion: What happened to Bitcoin?\nAnswer:", 
         "output": "Bitcoin's price rose by 10% following the ETF approval."},
        {"input": "Passage: Ethereum network upgrades reduce gas fees.\nQuestion: What change occurred on Ethereum?\nAnswer:", 
         "output": "Ethereum implemented an upgrade that lowered gas fees."},
        {"input": "Passage: Dogecoin rallies after Elon Musk tweets.\nQuestion: How did Dogecoin react?\nAnswer:", 
         "output": "Dogecoin's price surged following Elon Musk's tweet."},
        {"input": "Passage: Binance introduces staking rewards for BNB holders.\nQuestion: What did Binance do?\nAnswer:", 
         "output": "Binance started offering staking rewards for BNB holders."},
        {"input": "Passage: Cardano network announces smart contract launch.\nQuestion: What is new in Cardano?\nAnswer:", 
         "output": "Cardano launched smart contract functionality on its network."}
    ]
}


BASE_MODEL = "google/flan-t5-large"


for topic, examples in training_data.items():
    print(f"\n=== Fine-tuning for topic: {topic} ===\n")
    dataset = Dataset.from_list(examples)

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL)

    def preprocess(example):
        inputs = tokenizer(example["input"], truncation=True, padding="max_length", max_length=128)
        labels = tokenizer(example["output"], truncation=True, padding="max_length", max_length=64)
        inputs["labels"] = labels["input_ids"]
        return inputs

    tokenized_dataset = dataset.map(preprocess, remove_columns=["input", "output"])

    output_dir = f"./src/agents/specialized_agents/{topic}-generator"
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=2,
        num_train_epochs=3,
        logging_steps=5,
        save_steps=10,
        save_total_limit=2,
        learning_rate=5e-5,
        fp16=False,  # set True if using GPU
        logging_dir=f"{output_dir}/logs",
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )

    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Saved fine-tuned {topic} model to {output_dir}")
