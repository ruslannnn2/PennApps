import newspaper
import requests
response = requests.get("https://www.bbc.com/news/business-67470876")
print(response.status_code)




article = newspaper.build( 'https://www.bbc.com/news', memoize_articles=False)

for a in article.articles:
    print(a.url)