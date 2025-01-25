import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import csv
from datetime import datetime
import time
import matplotlib.pyplot as plt

# Replace with your API key or use scraping where APIs are not available.
NEWS_API_URL = "https://newsapi.org/v2/everything"
API_KEY = "eb502e6691104a25bc701ebddd52df61"

def fetch_articles(query, num_articles=250, from_date=None):
    """
    Fetches news articles containing the given query using NewsAPI.
    """
    articles = []
    page = 1
    while len(articles) < num_articles:
        params = {
            'q': query,
            'apiKey': API_KEY,
            'pageSize': 100,  # Max number of articles per page
            'page': page,
            'from': from_date
        }
        response = requests.get(NEWS_API_URL, params=params)
        if response.status_code == 429:  # Rate limit exceeded
            print("Rate limit exceeded. Waiting for 60 seconds...")
            time.sleep(60)
            continue
        elif response.status_code != 200:
            print(f"Error: {response.json().get('message', 'Unknown error')}")
            break
        data = response.json()
        if 'articles' not in data or not data['articles']:
            break
        articles.extend(data['articles'])
        page += 1
        if len(data['articles']) < 100:  # No more articles
            break
    return articles[:num_articles]

def extract_content(articles):
    """
    Extracts the content or description of articles, ensuring None values are handled.
    """
    return [(article.get('content') or '') + (article.get('description') or '') for article in articles]

def analyze_keywords(articles, keywords):
    """
    Analyzes the frequency of keywords in articles.
    """
    keyword_counts = Counter()
    total_articles = len(articles)
    articles_with_keywords = Counter()

    for content in articles:
        if content:  # Ensure content is not empty
            for keyword in keywords:
                occurrences = len(re.findall(rf'\b{keyword}\b', content, re.IGNORECASE))
                if occurrences > 0:
                    keyword_counts[keyword] += occurrences
                    articles_with_keywords[keyword] += 1

    return {
        'keyword_counts': keyword_counts,
        'articles_with_keywords': articles_with_keywords,
        'total_articles': total_articles
    }

def save_to_csv(results, output_filename):
    """
    Saves the keyword analysis results to a CSV file.
    """
    with open(output_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Keyword", "Total Occurrences", "Articles with Keyword", "Percentage of Total Articles"])

        for keyword, count in results['keyword_counts'].items():
            frequency = (results['articles_with_keywords'][keyword] / results['total_articles']) * 100
            writer.writerow([keyword, count, results['articles_with_keywords'][keyword], f"{frequency:.2f}%"])

def plot_keyword_chart(results):
    """
    Plots a bar chart for the keyword occurrences.
    """
    keywords = list(results['keyword_counts'].keys())
    occurrences = [results['keyword_counts'][keyword] for keyword in keywords]

    plt.figure(figsize=(10, 6))
    plt.barh(keywords, occurrences, color='skyblue')
    plt.xlabel('Total Occurrences')
    plt.title('Keyword Occurrences in News Articles')
    plt.tight_layout()  # To make sure everything fits without overlapping
    plt.savefig('keyword_occurrences_chart.png')  # Save the chart as an image
    plt.show()

def main():
    # Define the query and keywords
    query = (
        "'radical' OR terrorism OR 'extremists' AND politics OR election OR 'Donald Trump' OR Congress", "'Kamala Harris' OR 'Bernie Sanders' OR 'Pete Hegseth' OR 'Supreme Court'"
    )
    keywords = [
        'attack', 'attacked', 'assault', 'assaulted', 'batter', 'battered', 
        'beating', 'beaten', 'clash', 'clashed', 'fight', 'fought', 'punch', 
        'punched', 'kick', 'kicked', 'slap', 'slapped', 'stab', 'stabbed', 'shooting',
        'shot', 'killed', 'murder', 'murdered', 'killing', 'bloodbath', 'slaughter', 
        'torture', 'knives out', 'knock-out punch', 'came out swinging', 'show of force', 
        'stormed', 'war of words', 'battle', 'political battlefield', 'verbal assault', 
        'scorched earth', 'blitz', 'destroyed', 'crushed', 'smashed', 'obliterated', 
        'annihilated', 'fight back', 'take down', 'taken down', 'dismantle', 'wrecked', 
        'insurrection', 'riot', 'riots', 'riotous', 'uprising', 'storming', 'siege', 'mob', 
        'mobbed', 'armed conflict', 'civil unrest', 'rebellion', 'resistance', 'militia', 
        'extremist violence', 'armed group', 'political violence', 'political turmoil', 
        'protest violence', 'radical', 'extremists', 'attack on democracy', 'Capitol attack', 
        'Capitol storming', 'coup', 'coup attempt', 'rebellion', 'radicalization', 'domestic terrorism', 
        'terrorist attack', 'extremism', 'extremist groups', 'radical movements', 'radicalization', 
        'white nationalism', 'militia group', 'anti-government violence', 'far-right violence', 
        'far-left violence', 'violent extremism', 'bombings', 'explosive devices', 'hostage situation', 
        'armed standoff', 'police violence', 'law enforcement crackdown', 'police brutality', 'martial law', 
        'militarization', 'crackdown', 'excessive force', 'forceful tactics', 'riot police', 'barricades', 
        'national guard deployment', 'conflict', 'confrontation', 'division', 'polarization', 'partisan violence', 
        'social unrest', 'political fighting', 'violence at protests', 'civil disobedience', 'political crisis', 
        'political instability', 'state violence', 'authoritarian violence', 'regime violence', 'state repression'
    ]

    # Fixed start date
    start_date = "2024-12-31"

    # Number of articles to fetch
    num_articles = 100

    print(f"Fetching {num_articles} articles about '{query}' from {start_date} onwards...")
    articles = fetch_articles(query, num_articles=num_articles, from_date=start_date)

    if not articles:
        print("No articles found. Check your query or date range.")
        return

    print(f"Fetched {len(articles)} articles.")
    for i, article in enumerate(articles[:5], 1):  # Preview first 5 articles
        print(f"{i}. {article.get('title', 'No title')}, Source: {article.get('source', {}).get('name', 'Unknown')}")

    # Extract content and handle NoneType
    print("Extracting article content...")
    content_list = extract_content(articles)

    # Analyze keywords
    print("Analyzing keywords...")
    results = analyze_keywords(content_list, keywords)

    # Display results
    print("\nResults:")
    print(f"Total articles searched: {results['total_articles']}")
    print(f"Total keyword matches: {sum(results['keyword_counts'].values())}")

    print("\nKeyword Analysis:")
    for keyword, count in results['keyword_counts'].items():
        frequency = (results['articles_with_keywords'][keyword] / results['total_articles']) * 100
        print(f"Keyword '{keyword}':")
        print(f"  Total occurrences: {count}")
        print(f"  Articles with keyword: {results['articles_with_keywords'][keyword]} ({frequency:.2f}%)")

    # Save results to CSV
    save_to_csv(results, 'keyword_analysis_results.csv')
    print("\nResults saved to 'keyword_analysis_results.csv'.")

    # Generate and display the keyword chart
    plot_keyword_chart(results)

if __name__ == "__main__":
    main()
