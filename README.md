# NLP-Multi-Agent-System - Group 5

This project explores a multi-agent system for Natural Language Processing (NLP) tasks.
It has been developed as part of a group project (Group 5).

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

### 4. Create a .env file

Create a file named .env in the root directory of the project. This file stores environment variables such as API keys or other configuration settings needed for the project.

Start by copying the provided example file and filling in the required values:

cp .env.example .env   # macOS/Linux
copy .env.example .env # Windows

### 5. Setup Sample Dataset

#### Yahoo finance API
To test data access and prepare a small sample dataset from Yahoo Finance:

Run the provided script in tests/:

python tests/test_yahoo_access.py


This script downloads a small sample dataset and saves it locally in:

tests/data/

## 🧠 Description

The project implements a multi-agent NLP system where agents collaborate to process and analyze text data.
Each agent has a specific role (e.g., data preprocessing, model inference, evaluation).