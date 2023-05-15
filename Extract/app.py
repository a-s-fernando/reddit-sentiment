import os
import json
import praw
import datetime
import spacy
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import en_core_web_lg

load_dotenv()
nlp = en_core_web_lg.load()
sia = SentimentIntensityAnalyzer()  # Initialize Vader SentimentIntensityAnalyzer
NUM_POSTS = 2
SUBREDDIT_NAME = 'technology'

config = {
    "user_agent": os.environ.get("user_agent"),
    "client_id": os.environ.get("client_id"),
    "client_secret": os.environ.get("client_secret")
}

def fetch_posts(client_id: str, client_secret: str, user_agent: str, subreddit_name='technology', num_posts=1) -> list:
    """Function to fetch the top N posts from a subreddit"""
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    subreddit = reddit.subreddit(subreddit_name)
    hot_posts = subreddit.hot(limit=num_posts)

    posts_data: list[dict] = []

    for post in hot_posts:
        title = post.title.replace('/', ' or ')  # replace slashes with 'or' for Spacy recognition
        doc = nlp(title)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        print(entities)
        keywords = [ent[0] for ent in entities if ent[1] in ['ORG', 'LOC', 'PRODUCT']]
        post_data = {
            'id': post.id,
            'title': post.title,
            'entities': entities,
            'keywords': keywords,
            'datetime': str(datetime.datetime.utcfromtimestamp(post.created_utc)),
            'comments': []
        }

        posts_data.append(post_data)

    return posts_data

def analyse_comments(reddit, posts_data: list[dict]):
    """Function to analyse the sentiment and scores of comments in the given posts"""
    for post_data in posts_data:
        post = praw.models.Submission(reddit, id=post_data['id'])
        post.comments.replace_more(limit=0)

        for comment in post.comments.list():
            text = comment.body.replace('/', ' or ')  # replace slashes with 'or' for Spacy recognition
            doc = nlp(text)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            keywords = [ent[0] for ent in entities if ent[1] in ['ORG', 'LOC', 'PRODUCT']]
            sentiment = sia.polarity_scores(text)  # Use Vader to analyze sentiment
            post_data['comments'].append({
                'comment': text,
                'entities': entities,
                'keywords': keywords,
                'sentiment': sentiment,
                'datetime': str(datetime.datetime.utcfromtimestamp(comment.created_utc)),
                'score': comment.score
            })


def main():
    """Main function to run the script"""
    user_agent = config["user_agent"]
    client_id = config["client_id"]
    client_secret = config["client_secret"]

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    posts_data = fetch_posts(client_id, client_secret, user_agent, SUBREDDIT_NAME, NUM_POSTS)
    analyse_comments(reddit, posts_data)

    with open(f"{SUBREDDIT_NAME}_{NUM_POSTS}_posts.json", 'w') as f:
        json.dump(posts_data, f, indent=4)

# Run the main function
if __name__ == "__main__":
    main()
