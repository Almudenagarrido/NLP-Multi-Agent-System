# NLP-Multi-Agent-System - Group 5

This project explores the implementation of a **multi-agent system for Natural Language Processing (NLP)** tasks.  
It has been developed as part of a **university group project (Group 5)**.

The system is composed of several agents that collaborate to process and analyze text data.  
Each agent is responsible for a specific task within the NLP pipeline — such as **data preprocessing**, **information retrieval**, **model inference**, or **evaluation** — enabling modularity and cooperative problem solving.

## 🚀 Local Setup

Follow these steps to set up the project locally:

### 1. Clone the repository

 git clone https://github.com/Almudenagarrido/NLP-Multi-Agent-System
 cd NLP-Multi-Agent-System

### 2. Create and activate a virtual environment

 python3 -m venv venv  # macOS/Linux
 source venv/bin/activate

 python -m venv venv   # Windows
 venv\Scripts\activate

### 3. Install dependencies

 pip install -r requirements.txt

## ⚙️ Environment Configuration

### 📁 Create .env document

The project requires some configuration values to be stored in a .env file found in the directory of the project. This file stores environment variables such as API keys or other configuration settings needed for the project.

Start by copying the provided example file and filling in the required values:

 cp .env.example .env   # macOS/Linux
 copy .env.example .env # Windows

### 🔑 NewsAPI Key

The NewsRetrievalAgent uses NewsAPI to fetch financial and business news.

To enable this functionality:

1. Go to https://newsapi.org/register

2. Create a free account

3. You will receive an API key

4. Copy this key and paste it into your .env file:

 NEWS_API_KEY=your_api_key_here

 This key allows the agent to access the NewsAPI endpoint and fetch financial news.

## 🧪 Testing Access to Data Source

### 🔹Yahoo finance API
To test data access and prepare a small sample dataset from **Yahoo Finance**, run the provided script located in the tests/ directory:

 python tests/test_yahoo_access.py

### 🔹NewsAPI

To verify that your **NewsAPI** key is correctly set up and that the agent can fetch news articles, run:

 python tests/test_newsapi_access.py

Both these scripts will automatically create a small sample dataset and save it locally in:

 tests/data/

## 📰 News Retrieval Agent

The **NewsRetrievalAgent** collects recent financial news for predefined tickers from **Yahoo Finance** and **NewsAPI**.  
It merges and cleans the results, allowing export to **JSON**, **DataFrame**, or **CSV** formats.

### ⚙️ Dynamic Ticker Discovery

Automatically converts company names to stock symbols using real-time financial data from Yahoo Finance.

### ⚡ Quick Test

To test its functionality, open:

 src/agents/news_retrieval_agent.py

Set the variable:

 RUN_TEST = True

and run:

 python src/agents/news_retrieval_agent.py

This will retrieve sample news (e.g., AAPL, TSLA), print a summary in the terminal, and optionally save the data in data/raw/, as long as your .env file is correctly configured.

## ❤️ Sentiment Analysis Agent

The *SentimentAnalysisAgent* analyzes financial news content and classifies sentiment as **positive**, **negative**, or **neutral**. It uses specialized models trained on financial texts for accurate market sentiment detection.

### ⚡ Quick Test

To test its functionality, open:

 src/agents/sentiment_analysis_agent.py

Set the variable:

 RUN_TEST = True

and run:

 python src/agents/sentiment_analysis_agent.py

This will analyze sample financial news headlines, print sentiment tags with confidence scores in the terminal, and show the probability distribution for each classification.

## 📊 Evaluator Optimizer Agent

The EvaluatorOptimizerAgent provides quality assessment and actionable feedback for specialist responses. It evaluates responses based on multiple criteria including relevance, accuracy, completeness, context usage, and clarity, generating structured feedback to improve response quality.

### 🎯 Evaluation Criteria

- **Relevance**: Does the answer directly address the original query?

- **Accuracy**: Is the information factually correct based on news summaries?

- **Completeness**: Does it cover all aspects of the user's question?

- **Context Usage**: Does it leverage news, past Q&A, and SA label effectively?

- **Clarity**: Is the response clear and well-structured?

### ⚡ Quick Test

To test its functionality, open:

 src/agents/evaluator_optimizer_agent.py

Set the variable:

 RUN_TEST = True

and run:

 python src/agents/evaluator_optimizer_agent.py

This will run a sample evaluation on a test response, printing the overall score, critical issues, strengths, and actionable feedback in a structured JSON format.

## 🧠 Train the Specialized Agents

From the project’s main folder, run:

 python src/agents/specialized_agents_training.py

This will create topic-specific generator models inside:

 src/agents/specialized_agents/

The current base model being fine-tuned is:

 google/flan-t5-large

## 🧩 Running the Full Pipeline

Once the agents have been trained and the environment is configured, you can execute the full system flow.

### ▶️ Steps

Open and run the main notebook:

 src/main/outline.ipynb

This notebook demonstrates the complete workflow:
  → user query → topic classification → response generation → answer storage