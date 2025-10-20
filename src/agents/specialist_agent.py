from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class Specialist:
    def __init__(self, topic, base_dir="../agents/specialized_agents"):
        self.topic = topic
        self.model_path = f"{base_dir}/{topic}-generator"
        print(f"Loading model for topic: {topic} from {self.model_path}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, use_fast=False)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path)
        self.model.eval()
        if torch.cuda.is_available():
            self.model.to("cuda")
            print("Using GPU")
        else:
            print("Using CPU")

    def respond(self, query, news_summaries, past_queries, feedback="", SA_label=""):
        past_qas = "\n".join([f"Q: {pq['question']}\nA: {pq['answer']}" for pq in past_queries])
        news_context = "\n".join(news_summaries)
        
        prompt = f"""You are a domain-specific assistant for {self.topic}.

Query: {query}

News Summaries:
{news_context}

Past Queries and Answers:
{past_qas}

Feedback: {feedback}
SA_label: {SA_label}

Answer the query based on the above context."""
        
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, padding="max_length", max_length=1024)
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        
        outputs = self.model.generate(**inputs, max_new_tokens=512)
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer.strip(), prompt
