"""Unit tests to ensure the correct functionality of the app.py script"""
import os
from dotenv import load_dotenv
import praw
import spacy
import unittest
from unittest.mock import MagicMock
from app import fetch_posts, analyse_comments


# Load environment variables from .env file
load_dotenv('.env')

def test_fetch_posts_returns_list_of_dictionaries():
    """Tests if the returned data is a list of dictionaries"""
    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')
    user_agent = os.getenv('user_agent')

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    posts = fetch_posts(reddit)
    assert isinstance(posts, list)
    assert all(isinstance(post, dict) for post in posts)

def test_fetch_posts_returns_correct_number_of_posts():
    """Tests if the number of returned posts matches up with the desired number"""
    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')
    user_agent = os.getenv('user_agent')

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    num_posts = 2
    posts = fetch_posts(reddit, num_posts=num_posts)
    assert len(posts) == num_posts

def test_fetch_posts_returns_post_dictionary_with_required_keys():
    """Tests if the returned output is a dict and includes all required keys"""
    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')
    user_agent = os.getenv('user_agent')

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    posts = fetch_posts(reddit)
    required_keys = ['id', 'title', 'entities', 'keywords', 'datetime', 'comments']
    assert all(set(required_keys).issubset(post.keys()) for post in posts)

def test_fetch_posts_returns_post_with_correct_types():
    """Tests that the returned output for entities and keywords are of the correct type"""
    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')
    user_agent = os.getenv('user_agent')

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )
    posts = fetch_posts(reddit)
    nlp = spacy.load('en_core_web_lg')  # Load spaCy model

    posts = fetch_posts(reddit)
    for post in posts:
        entities = post['entities']
        print(entities)
        keywords = post['keywords']
        title = post['title']
        doc = nlp(title)
        extracted_entities = [(ent.text, ent.label_) for ent in doc.ents]
        extracted_keywords = [ent[0] for ent in extracted_entities if ent[1] in ['ORG', 'LOC', 'PRODUCT']]
        assert type(entities) == list
        assert type(keywords) == list


import unittest
from unittest.mock import MagicMock, patch
from app import analyse_comments

class AnalyseCommentsTestCase(unittest.TestCase):
    def setUp(self):
        # Mock praw.Reddit object
        self.reddit = MagicMock()

    @patch('app.praw.models')
    def test_analyse_comments_adds_comments_to_post_data(self, mock_models):
        # Mock post_data dictionary
        post_data = {
            'id': '123456',
            'title': 'Sample Post',
            'entities': [],
            'keywords': [],
            'datetime': '2023-05-01 12:00:00',
            'comments': []
        }

        # Mock praw.models.Submission object
        mock_submission = MagicMock()
        mock_models.Submission.return_value = mock_submission

        # Mock praw.models.Comment objects
        mock_comment1 = MagicMock()
        mock_comment1.body = "First comment"
        mock_comment2 = MagicMock()
        mock_comment2.body = "Second comment"
        mock_submission.comments.list.return_value = [mock_comment1, mock_comment2]

        # Call analyse_comments function
        analyse_comments(self.reddit, post_data)

        # Assertions
        self.assertEqual(len(post_data['comments']), 2)
        self.assertEqual(post_data['comments'][0]['comment'], "First comment")
        self.assertEqual(post_data['comments'][1]['comment'], "Second comment")

    @patch('app.praw.models')
    def test_analyse_comments_extract_entities_and_keywords(self, mock_models):
        # Mock post_data dictionary with a single comment
        post_data = {
            'id': '123456',
            'title': 'Sample Post',
            'entities': [],
            'keywords': [],
            'datetime': '2023-05-01 12:00:00',
            'comments': []
        }
        mock_comment = MagicMock()
        mock_comment.body = "I love using Reddit. It's great!"
        mock_models.Submission.return_value.comments.list.return_value = [mock_comment]

        # Call analyse_comments function
        analyse_comments(self.reddit, post_data)

        # Assertions
        self.assertEqual(len(post_data['comments']), 1)
        self.assertNotEqual(len(post_data['comments'][0]['entities']), 0)
        self.assertNotEqual(len(post_data['comments'][0]['keywords']), 0)

    @patch('app.praw.models')
    def test_analyse_comments_calculate_sentiment_scores(self, mock_models):
        # Mock post_data dictionary with a single comment
        post_data = {
            'id': '123456',
            'title': 'Sample Post',
            'entities': [],
            'keywords': [],
            'datetime': '2023-05-01 12:00:00',
            'comments': []
        }
        mock_comment = MagicMock()
        mock_comment.body = "I love using Reddit. It's great!"
        mock_models.Submission.return_value.comments.list.return_value = [mock_comment]

        # Call analyse_comments function
        analyse_comments(self.reddit, post_data)

        # Assertions
        self.assertEqual(len(post_data['comments']), 1)
        self.assertIsNotNone(post_data['comments'][0]['sentiment'])
        self.assertIsInstance(post_data['comments'][0]['sentiment'], dict)
        self.assertIn('compound', post_data['comments'][0]['sentiment'])
        self.assertIn('pos', post_data['comments'][0]['sentiment'])
        self.assertIn('neg', post_data['comments'][0]['sentiment'])
        self.assertIn('neu', post_data['comments'][0]['sentiment'])



