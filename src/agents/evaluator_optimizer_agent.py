import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class EvaluatorOptimizer:

    def __init__(self, model_name="HuggingFaceH4/zephyr-7b-alpha"):
                
        self.evaluation_criteria = {
            "relevance": "Does the answer directly address the original query?",
            "accuracy": "Is the information factually correct based on news summaries?",
            "completeness": "Does it cover all aspects of the user's question?",
            "context_usage": "Does it properly leverage news summaries, past Q&A, and SA label?",
            "clarity": "Is the response clear, well-structured and easy to understand?"
        }
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model.eval()
        
        if torch.cuda.is_available():
            self.model.to("cuda")
    
    def evaluate_response(self, original_query, news_summaries, past_queries, specialist_response, SA_label, specialist_prompt):
        
        prompt = self._create_evaluation_prompt(
            original_query, news_summaries, past_queries, 
            specialist_response, SA_label, specialist_prompt
        )
        
        llm_output = self._generate_evaluation(prompt)
        
        try:
            evaluation = json.loads(llm_output)
        except:
            evaluation = llm_output
        
        return evaluation
    
    def _create_evaluation_prompt(self, original_query, news_summaries, past_queries, specialist_response, SA_label, specialist_prompt):

        prompt = f"""
You are an expert response evaluator. Your task is to analyze the specialist's response and provide CONCRETE, ACTIONABLE feedback to improve THIS specific response.

EVALUATION CONTEXT:
ORIGINAL QUERY: {original_query}

NEWS SUMMARIES:
{chr(10).join(news_summaries)}

PAST QUERIES & ANSWERS:
{chr(10).join([f"Q: {pq['question']} | A: {pq['answer']}" for pq in past_queries])}

SA LABEL: {SA_label}

SPECIALIST'S RESPONSE:
{specialist_response}

PROMPT USED BY SPECIALIST:
{specialist_prompt}

EVALUATION CRITERIA:
1. RELEVANCE: Does it directly answer the original query?
2. ACCURACY: Is it factually correct based on news summaries?
3. COMPLETENESS: Does it address all parts of the query?
4. CONTEXT USAGE: Does it leverage news, past Q&A, and SA label effectively?
5. CLARITY: Is the response clear and well-structured?

OUTPUT FORMAT (JSON only):
{{
    "overall_score": 0-100,
    "critical_issues": ["list of main problems that need fixing"],
    "strengths": ["what was done well in this response"],
    "actionable_feedback": "concrete instructions to improve THIS specific response"
}}

Be brutally honest and specific. Focus on what can be improved in THIS response.
"""
        return prompt

    def _generate_evaluation(self, prompt):
        
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        
        inputs = self.tokenizer(formatted_prompt, return_tensors="pt", truncation=True, max_length=2048)
        
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        if "[/INST]" in response:
            response = response.split("[/INST]")[1].strip()
        
        return response


def test_evaluator():
    print("🧪 Testing EvaluatorOptimizer...")
    
    original_query = "How are Apple's stocks performing?"
    news_summaries = [
        "Apple reported strong earnings with 15% revenue growth",
        "New iPhone sales exceeded expectations in Q3"
    ]
    past_queries = [
        {"question": "What is Apple's market cap?", "answer": "Apple's market cap is around $2.8 trillion"}
    ]
    specialist_response = "Apple stocks are doing well with positive earnings."
    SA_label = "positive"
    specialist_prompt = "You are a financial specialist. Answer based on the news."
    
    evaluator = EvaluatorOptimizer()
    
    print("📊 Running evaluation...")
    result = evaluator.evaluate_response(
        original_query=original_query,
        news_summaries=news_summaries,
        past_queries=past_queries,
        specialist_response=specialist_response,
        SA_label=SA_label,
        specialist_prompt=specialist_prompt
    )
    
    print("\n✅ Evaluation Result:")
    print(f"Type: {type(result)}")
    if isinstance(result, dict):
        for key, value in result.items():
            print(f"{key}: {value}")
    else:
        print(f"Raw output: {result}")


if __name__ == "__main__":
    RUN_TEST = True
    
    if RUN_TEST:
        test_evaluator()