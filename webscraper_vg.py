import requests
from bs4 import BeautifulSoup
import json
import time

# Globale variabler for å lagre tidligere sett artikler
last_seen_articles = set()

def fetch_articles():
    # URL to VG's front page
    url = 'https://www.vg.no'

    # Perform a GET request to VG
    response = requests.get(url)
    response.raise_for_status()  # Checks if the request was successful

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all script elements that contain the data we want to extract
    articles = soup.find_all('article')

    new_articles = []

    # Process each script element found
    for article in articles:
        #Find title
        title_tag = article.find('h2')
        if not title_tag:
            continue
        title = title_tag.get('aria-label', 'Ingen tidspunkt')
        
        #Find script tag within article
        script_element = article.find('script', type='application/json')

        #If script element is found
        if script_element:
            #Extract string from element
            json_str = script_element.string
            try:
                #Parse json string
                data = json.loads(json_str)
                published = data.get('changes', {}).get('published', 'Ukjent publiseringstidspunkt')
                word_count = data.get('wordCount', 0)
                brand = data.get('brand')
            except:
                published = "Ukjent publiserinstidspunkt"
                word_count = 0
                brand = "Ukjent"
        
        a_tag = article.find('a', itemprop='url')
    
        # Check if the a_tag exists and has an 'href' attribute
        if a_tag and a_tag.has_attr('href'):
            # Extract the URL
            url = a_tag['href']
            # Make a GET request to the URL
            response = requests.get(url)
            response.raise_for_status()  # Will raise an error if the request failed

            # Parse the HTML content of the article page
            soup_article = BeautifulSoup(response.content, 'html.parser')
            #Find ingress
            ingress_tag = soup_article.find('p', class_='fullWidth addGutters hyperion-css-16eu8tf')
            ingress = ingress_tag.get_text().strip() if ingress_tag else 'Ingress ikke funnet'
            
        #Check if title has been seen
        if title not in last_seen_articles:
            last_seen_articles.add(title)
            # Add to the list of new articles
            new_articles.append((title, published, word_count, brand, ingress))
        
    #Return the list of new articles
    return new_articles

def main():
    print("Starter skraping av VGs forside. Trykk CTRL+C for å avslutte.")
    try:
        while True:
            # Fetch new articles since last check
            new_articles = fetch_articles()
            
            # If there are new articles, print them
            if new_articles:
                print(f"Fant {len(new_articles)} nye artikler:")
                for article in new_articles:
                    print(f"Tittel: {article[0]}")
                    print(f"Publisert: {article[1]}")
                    print(f"Word count: {article[2]}")
                    print(f"Brand: {article[3]}")
                    print(f"Ingress: {article[4]}")
                    print("-------------------------------")
            else:
                print("Ingen nye artikler siden sist.")
            
            # Wait for 60 seconds before next scrape
            time.sleep(60)
    except KeyboardInterrupt:
        print("Avslutter skraperen.")

if __name__ == "__main__":
    main()