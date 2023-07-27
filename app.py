import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import statistics
import questionary
import validators


console = Console()
table = Table(leading=2)
table2 = Table(leading=2)
sentiment = SentimentIntensityAnalyzer()


def evaluate_sentiment(sentiment_score):
    if sentiment_score >= 0.05:
        return "POSITIVE"

    elif sentiment_score <= -0.05:
        return "NEGATIVE"
    
    else:
        return "NEUTRAL"


url = questionary.text("Enter the URL of the product: ").ask()

if not validators.url(url) or "flipkart" in url:
    console.log("Invalid URL!!")
    exit(1)
    
response = requests.get("https://www.flipkart.com/nvidia-rtx-3060-gaming-oc-12gb-lhr-graphics-card-rev-2-0-gv-n3060gaming-oc-12gd-12-gb-gddr6/p/itm210baad01a2a6?pid=GRCGHS6SSVJDGNBP&lid=LSTGRCGHS6SSVJDGNBPBWELYI&marketplace=FLIPKART&q=graphics+card&store=6bo%2Fg0i%2F6sn&srno=s_1_12&otracker=AS_Query_PredictiveAutoSuggest_3_0_na_na_na&otracker1=AS_Query_PredictiveAutoSuggest_3_0_na_na_na&fm=search-autosuggest&iid=7f1ebf5c-24b4-4ae2-afee-38126fa92b03.GRCGHS6SSVJDGNBP.SEARCH&ppt=sp&ppn=sp&qH=ae2a487734c75ca2")

soup = BeautifulSoup(response.content, "html.parser")


product = soup.find(class_="B_NuCI").text
currentprice = soup.find(class_="_30jeq3").text

try:
    ratings = soup.find(class_="_2d4LTz").text
    reviews = {}
    review_sentiment_scores = []

except:
    console.log("Insufficient information available!!")
    exit(1)

for review, users in zip(soup.findAll("div", class_="t-ZTKy"), soup.findAll("p", class_="_2V5EHH")):
    reviews.update(
        {
            users.text: review.text.replace("READ MORE", "")
        }
    )
    review_sentiment_scores.append(sentiment.polarity_scores(review.text)["compound"])


review_sentiment_score = statistics.mean(review_sentiment_scores)

table.add_column("Information", justify="left", style="magenta")
table.add_column("Value", justify="left", style="cyan")

table.add_row("Product", product)
table.add_row("Current Price", currentprice)
table.add_row("Ratings", str(ratings))
table.add_row("Overall Sentiment", evaluate_sentiment(sentiment_score=review_sentiment_score))
table.add_row("Sentiment Score", str(review_sentiment_score))

console.print(table)


confirm = questionary.confirm("Would you like to view customer reviews?").ask()

if confirm:
    table2.add_column("Username", justify="left", style="magenta")
    table2.add_column("Review", justify="left", style="cyan")

    for user in reviews.keys():
        table2.add_row(user, reviews[user])

    console.print(table2)