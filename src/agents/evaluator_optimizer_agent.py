import torch
from sentence_transformers import SentenceTransformer, util
import numpy as np

class EvaluatorOptimizer:

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        
        self.model = SentenceTransformer(model_name)
        if torch.cuda.is_available():
            self.model = self.model.to("cuda")

        self.evaluation_criteria = ["relevance", "accuracy", "completeness", "context_usage", "clarity"]

    def evaluate_response(self, original_query, news_summaries, past_queries, specialist_response):

        query_emb = self.model.encode(original_query, convert_to_tensor=True)
        response_emb = self.model.encode(specialist_response, convert_to_tensor=True)
        relevance_score = util.pytorch_cos_sim(response_emb, query_emb).item()

        if news_summaries:
            news_text = " ".join(news_summaries)
            news_emb = self.model.encode(news_text, convert_to_tensor=True)
            accuracy_score = util.pytorch_cos_sim(response_emb, news_emb).item()
        else:
            accuracy_score = 0.5

        context_parts = []
        if news_summaries:
            context_parts.extend(news_summaries)
        if past_queries:
            context_parts.extend([f"{p['question']} {p['answer']}" for p in past_queries])
        
        if context_parts:
            context_text = " ".join(context_parts)
            context_emb = self.model.encode(context_text, convert_to_tensor=True)
            context_score = util.pytorch_cos_sim(response_emb, context_emb).item()
        else:
            context_score = 0.3
        
        words = specialist_response.split()
        completeness_score = min(1.0, len(words) / 50)
        unique_words = len(set(words))
        diversity_score = min(1.0, unique_words / max(1, len(words)))
        completeness_score = (completeness_score + diversity_score) / 2

        sentences = specialist_response.split('.')
        if len(sentences) > 1:
            sentence_embs = self.model.encode([s.strip() for s in sentences if s.strip()])
            clarity_scores = []
            for i in range(len(sentence_embs)-1):
                sim = util.pytorch_cos_sim(
                    torch.tensor(sentence_embs[i]).unsqueeze(0), 
                    torch.tensor(sentence_embs[i+1]).unsqueeze(0)
                ).item()
                clarity_scores.append(sim)
            clarity_score = np.mean(clarity_scores) if clarity_scores else 0.7
        else:
            clarity_score = 0.6

        scores = {
            "relevance": int(relevance_score * 100),
            "accuracy": int(accuracy_score * 100),
            "completeness": int(completeness_score * 100),
            "context_usage": int(context_score * 100),
            "clarity": int(clarity_score * 100),
            "overall_score": int((relevance_score + accuracy_score + context_score + completeness_score + clarity_score) / 5 * 100)
        }

        feedback_parts = []
        if relevance_score < 0.5:
            feedback_parts.append("Response could better address the original question.")
        if accuracy_score < 0.4:
            feedback_parts.append("Consider incorporating more specific data from the news.")
        if context_score < 0.3:
            feedback_parts.append("Make better use of the available context and history.")
        if completeness_score < 0.6:
            feedback_parts.append("Response could be more comprehensive and detailed.")
        if clarity_score < 0.6:
            feedback_parts.append("Improve clarity and logical flow between ideas.")
        
        if not feedback_parts:
            feedback_parts.append("Good overall alignment with context and query.")

        feedback = " ".join(feedback_parts)

        return {
            "overall_score": scores["overall_score"],
            "dimension_scores": scores,
            "critical_issues": [fb for fb in feedback_parts if any(word in fb.lower() for word in ["could", "consider", "improve", "better"])],
            "strengths": [fb for fb in feedback_parts if "good" in fb.lower()],
            "actionable_feedback": feedback
        }


def test_evaluator():
    print("🧪 Testing Enhanced EvaluatorOptimizer")
    print("="*50)

    print("📊 Test 1 - Good response")
    original_query = "How are Apple's stocks performing?"
    news_summaries = ["Apple reported strong earnings with 15% revenue growth in Q4 2024"]
    past_queries = [
        {"question": "What is Apple's market cap?", "answer": "Apple's market cap is around $2.8 trillion"}
    ]
    specialist_response = "Apple stocks are performing very well with strong earnings growth of 15% and positive market sentiment. The company continues to show robust financial performance."

    evaluator = EvaluatorOptimizer()
    result = evaluator.evaluate_response(
        original_query=original_query,
        news_summaries=news_summaries,
        past_queries=past_queries,
        specialist_response=specialist_response
    )

    print("\n✅ Evaluation Result:")
    for key, value in result.items():
        print(f"{key}: {value}")

    print("\n" + "="*50)
    print("📊 Test 2 - Poor response")
    bad_response = "The weather is nice today. I like coffee."
    result2 = evaluator.evaluate_response(
        original_query=original_query,
        news_summaries=news_summaries,
        past_queries=past_queries,
        specialist_response=bad_response
    )

    print("\n❌ Evaluation Result:")
    for key, value in result2.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    RUN_TEST = False

    if RUN_TEST:
        test_evaluator()