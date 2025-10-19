# 🧠 NLP Multi-Agent News System

## ⚙️ Setup
Before running the project, make sure to install the required tokenizers:
```bash
pip install sentencepiece tiktoken

🚀 Usage

Train the specialized agents
From the project’s main folder, run:

python src/agents/specialized_agents_training.py


This will create the topic-specific generator models inside:

src/agents/specialized_agents/


The current base model being fine-tuned is:

google/flan-t5-large


Run the main pipeline
Open and execute the notebook:

src/main/outline.ipynb


This notebook goes through the entire flow —
from user query → topic classification → response generation → answer storage.
(Evaluation is not yet included.)

✅ Summary:

Install dependencies (sentencepiece, tiktoken)

Fine-tune agents with specialized_agents_training.py

Run full pipeline with outline.ipynb
