"""Script to extract data from reddit using PRAW, and send it to an S3 bucket"""
import os
import json
import datetime
import praw
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import en_core_web_lg
import nltk
import boto3

nltk.data.path.append("/tmp")
nltk.download("vader_lexicon", download_dir="/tmp")
load_dotenv()

nlp = en_core_web_lg.load()
sia = SentimentIntensityAnalyzer()  # Initialise Vader SentimentIntensityAnalyzer
NUM_POSTS = os.environ.get("num_posts")
SUBREDDIT_NAME = os.environ.get("subreddit_name")

config = {
    "user_agent": os.environ.get("user_agent"),
    "client_id": os.environ.get("client_id"),
    "client_secret": os.environ.get("client_secret")
}


def fetch_posts(reddit: praw.Reddit, subreddit_name='technology', num_posts=1) -> list:
    """Function to fetch the top N posts from a subreddit"""
    print("Fetching posts...")
    subreddit = reddit.subreddit(subreddit_name)
    hot_posts = subreddit.hot(limit=int(num_posts))

    posts_data: list[dict] = []

    for post in hot_posts:
        # replace slashes with 'or' for Spacy recognition
        title = post.title.replace('/', ' or ')
        doc = nlp(title)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        adjectives = [token.text for token in doc if token.pos_ == 'ADJ']
        keywords = [ent[0]
                    for ent in entities if ent[1] in ['ORG', 'LOC', 'PRODUCT']]
        post_data = {
            'id': post.id,
            'title': post.title,
            'entities': entities,
            'keywords': keywords + adjectives,
            'datetime': str(datetime.datetime.utcfromtimestamp(post.created_utc)),
            'comments': []
        }

        # Analyze comments for each post
        analyse_comments(reddit, post_data)

        posts_data.append(post_data)

    return posts_data


def analyse_comments(reddit: praw.Reddit, post_data: dict):
    """Function to analyze the sentiment and scores of comments in the given post"""
    post = praw.models.Submission(reddit, id=post_data['id'])
    post.comments.replace_more(limit=0)

    for comment in post.comments.list():
        # replace slashes with 'or' for Spacy recognition
        text = comment.body.replace('/', ' or ')
        doc = nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        adjectives = [token.text.lower()
                      for token in doc if token.pos_ == 'ADJ']
        keywords = [ent[0].lower() for ent in entities if ent[1]
                    in ['ORG', 'LOC', 'PRODUCT']]
        sentiment = sia.polarity_scores(text)  # Use Vader to analyze sentiment
        post_data['comments'].append({
            'comment': text,
            'keywords': keywords + adjectives,
            'sentiment': sentiment,
            'datetime': str(datetime.datetime.utcfromtimestamp(comment.created_utc)),
            'score': comment.score
        })


def lambda_handler(event, context):
    """AWS Lambda handler function"""
    user_agent = config["user_agent"]
    client_id = config["client_id"]
    client_secret = config["client_secret"]

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    # Check if the Reddit API is connecting properly
    if reddit.read_only:
        print("Successfully connected to the Reddit API")
    else:
        print("Failed to connect to the Reddit API")
        return None # Terminate the script if the API connection failed

    posts_data = fetch_posts(reddit, SUBREDDIT_NAME, NUM_POSTS)

    print("Connecting to bucket...")
    s3 = boto3.resource(service_name='s3', region_name=os.environ.get("region_name"),
                        aws_access_key_id=os.environ.get("access_key"),
                        aws_secret_access_key=os.environ.get("secret_access_key"))
    bucket_name = os.environ.get("bucket_name")
    file_name = "posts_data.json"

    print("Uploading file...")
    s3.Bucket(bucket_name).put_object(
        Key=file_name, Body=json.dumps(posts_data))

    # Return the posts_data as the response

    print("File uploaded.")
    return "Sent data to S3."
