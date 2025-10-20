import re
import os
import nltk
import torch
from dataclasses import dataclass
from typing import Literal, Optional, List, Dict
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
try:
    from nltk.sentiment import SentimentIntensityAnalyzer
except LookupError:
    nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer

Label = Literal["positive", "negative", "neutral"]

@dataclass
class SentimentResult:
    id: Optional[str]
    label: Label
    score: float
    distribution: Dict[Label, float]
    explanation: Optional[str] = None

_WS = re.compile(r"\s+")

def clean_text(text):
    text = text.strip()
    text = _WS.sub(" ", text)
    return text

class _HFBackend:
    
    def __init__(self, model_name="yiyanghkust/finbert-tone"):
        try:
            torch.manual_seed(42)
        except Exception:
            pass
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.pipe = TextClassificationPipeline(model=self.model, tokenizer=self.tokenizer, top_k=None, truncation=True)

    def predict(self, texts):
        outputs = self.pipe(texts)
        results: List[SentimentResult] = []
        for scores in outputs:
            dist_map: Dict[Label, float] = {"negative": 0.0, "neutral": 0.0, "positive": 0.0}
            for s in scores:
                lab = s["label"].lower()
                if lab in dist_map:
                    dist_map[lab] = float(s["score"])
            label: Label = max(dist_map, key=dist_map.get)
            score: float = float(dist_map[label])
            results.append(SentimentResult(id=None, label=label, score=score, distribution=dist_map))
        return results

class _VADERBackend:
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def predict(self, texts):
        return [self._score_one(t) for t in texts]
    
    def _score_one(self, text):
        s = self.analyzer.polarity_scores(text)
        dist: Dict[Label, float] = {
            "negative": float(s.get("neg", 0.0)),
            "neutral": float(s.get("neu", 0.0)),
            "positive": float(s.get("pos", 0.0)),
        }
        label: Label = max(dist, key=dist.get)
        score = float(dist[label])
        return SentimentResult(id=None, label=label, score=score, distribution=dist)

class SentimentAnalysisAgent:
    
    def __init__(self, model_preference=None, model_name=None):
        self.backend_name = None
        self.backend = None
        pref = (model_preference or os.getenv("SENTIMENT_BACKEND") or "auto").lower()
        if pref in ("transformers", "auto"):
            try:
                self.backend = _HFBackend(model_name or os.getenv("FINBERT_MODEL", "yiyanghkust/finbert-tone"))
                self.backend_name = "transformers"
            except Exception as e:
                if pref == "transformers":
                    raise
        if self.backend is None:
            self.backend = _VADERBackend()
            self.backend_name = "vader"

    def _best_sentence_explanation(self, text):
        sents = re.split(r"(?<=[.!?])\s+", text.strip())
        sents = [s for s in sents if s]
        if len(sents) <= 1:
            return text[:280]
        sub = self.backend.predict(sents)
        def mag(r: SentimentResult) -> float:
            return abs(r.distribution.get("positive",0.0) - r.distribution.get("negative",0.0))
        best = max(zip(sents, sub), key=lambda p: mag(p[1]))
        return best[0][:280]

    def predict_one(self, text, *, id=None) -> SentimentResult:
        text = clean_text(text)
        res = self.backend.predict([text])[0]
        return SentimentResult(
            id=id,
            label=res.label,
            score=float(res.score),
            distribution={k: float(v) for k, v in res.distribution.items()},
            explanation=self._best_sentence_explanation(text)
        )

    def predict_batch(self, texts, *, ids=None):
        texts = [clean_text(t) for t in texts]
        raw = self.backend.predict(texts)
        out: List[SentimentResult] = []
        for i, r in enumerate(raw):
            rid = ids[i] if ids and i < len(ids) else None
            expl = self._best_sentence_explanation(texts[i])
            out.append(SentimentResult(id=rid, label=r.label, score=float(r.score), distribution={k: float(v) for k, v in r.distribution.items()}, explanation=expl))
        return out


def test_sentiment_agent():
    
    print("🧠 Testing Sentiment Analysis Agent...")
    agent = SentimentAnalysisAgent()
    
    samples = [
        "Apple beats earnings expectations; revenue rises 12% year-over-year.",
        "Tesla shares drop 5% after disappointing delivery numbers.",
        "The market remained stable with minimal fluctuations today."
    ]
    
    for i, sample in enumerate(samples):
        result = agent.predict_one(sample, id=f"test_{i}")
        print(f"\n📝 Sample {i+1}: {sample}")
        print(f"🎯 Result: {result.label} (score: {result.score:.3f})")
        print(f"📊 Distribution: {result.distribution}")
    
    print(f"\n✅ Backend used: {agent.backend_name}")

if __name__ == "__main__":
    RUN_TEST = False
    
    if RUN_TEST:
        test_sentiment_agent()