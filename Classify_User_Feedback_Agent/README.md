An AI-powered product feedback classifier that analyzes app reviews using Cohere’s Command-A to generate categories, sentiment, severity, and PM-ready summaries, then exports everything into a structured CSV.

This script is a Feedback Classifier Agent that:
- Reads App Store reviews from a CSV
- Sends each review to Cohere’s Command-A model
- The model performs full intelligence:
- Category classification
- Sentiment analysis
- Severity scoring
- PM summary generation
- The script then saves structured results into a new CSV.
