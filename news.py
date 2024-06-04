import os
import requests
from transformers import pipeline
import time
from datetime import datetime

def fetch_news(api_key, query, language='en'):
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': query,
        'language': language,
        'apiKey': api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        return articles
    else:
        print(f"Failed to fetch news: {response.status_code}")
        return []

def summarize_article(article, summarizer):
    title = article.get('title', 'No Title')
    content = article.get('content', '') or article.get('description', '')
    if not content:
        content = article.get('url', 'No Content')
    
    summary = summarizer(content, max_length=100, min_length=30, do_sample=False)
    return {
        'title': title,
        'summary': summary[0]['summary_text']
    }

def save_article(title, summary, category):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{title}_{timestamp}.txt"
    filepath = os.path.join(category, filename)
    with open(filepath, 'w') as file:
        file.write(summary)

def main():
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        raise ValueError("NEWS_API_KEY environment variable is not set")
    
    interests = ['gaming', 'anime', 'schools', 'crime', 'nintendo', 'playstation', 'xbox', 'steam']
    query = ' OR '.join(interests)
    summarizer = pipeline('summarization')

    while True:
        articles = fetch_news(api_key, query)
        for article in articles:
            summarized_article = summarize_article(article, summarizer)
            category = 'other'
            for interest in interests:
                if interest in article['title'].lower() or (article['description'] and interest in article['description'].lower()):
                    category = interest
                    break
            save_article(article['title'], summarized_article['summary'], category)
        time.sleep(3600)  # Run every hour

if __name__ == "__main__":
    main()
