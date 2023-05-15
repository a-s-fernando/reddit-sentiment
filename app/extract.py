import json
import praw
import datetime
from textblob import TextBlob
import spacy

def fetch_and_analyse_comments(client_id: str, client_secret: str, user_agent: str, subreddit_name='technology', num_posts=1):
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    nlp = spacy.load('en_core_web_sm')

    subreddit = reddit.subreddit(subreddit_name)
    hot_posts = subreddit.hot(limit=num_posts)

    posts_data = []

    for post in hot_posts:
        post_data = {
            'title': post.title,
            'keywords': [token.text for token in nlp(post.title) if not token.is_stop and not token.is_punct],
            'datetime': str(datetime.datetime.utcfromtimestamp(post.created_utc)),
            'comments': []
        }

        post.comments.replace_more(limit=0)
        for comment in post.comments.list():
            text = comment.body
            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity
            post_data['comments'].append({
                'comment': text,
                'sentiment': sentiment,
                'datetime': str(datetime.datetime.utcfromtimestamp(comment.created_utc)),
                'score': comment.score
            })

        posts_data.append(post_data)

    with open(f"{subreddit_name}_{num_posts}_posts.json", 'w') as f:
        json.dump(posts_data, f, indent=4)



def main():
    user_agent = "Scraper 1.0 by /u/Responsible_Coach877"
    client_id = "MpxjMuBRhV7gsHMOmhWSyw"
    client_secret = "4x2lKHUhOvBkvm2JdLA8FZuK6S-C_Q"

    fetch_and_analyse_comments(client_id, client_secret, user_agent, 'technology', 10)

# Run the main function
main()
