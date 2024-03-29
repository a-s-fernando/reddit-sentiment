"""Test file for the load.py script"""
import os
import unittest
import psycopg2
from load import lambda_handler
from dotenv import load_dotenv

load_dotenv()

class TestLoad(unittest.TestCase):
    """Class to test the load functions"""
    def setUp(self):
        self.db_host = os.environ.get('DB_HOST')
        self.db_port = os.environ.get('DB_PORT')
        self.db_name = os.environ.get('DB_NAME')
        self.db_user = os.environ.get('DB_USER')
        self.db_password = os.environ.get('DB_PASSWORD')

        # Create test data
        self.test_data = [
            {"title": "test title", "datetime": "2023-05-22", "keywords": ["test"],
            "comments": [{"comment": "test comment", "datetime": "2023-05-22",
            "score": 1, "sentiment": {"compound": 1}, "keywords": ["test"]}]}
            ]

        # Setup database connection
        self.conn = psycopg2.connect(host=self.db_host,
                                     port=self.db_port,
                                     dbname=self.db_name,
                                     user=self.db_user,
                                     password=self.db_password)

        self.cursor = self.conn.cursor()

    def tearDown(self):
        if "amazonaws" in self.db_host:
            raise ValueError("Testing on the production db!")
        # Clean up database
        self.cursor.execute(
            "DROP TABLE IF EXISTS Post, Post_keyword, Keyword_in_post, Comment, Comment_keyword, Keyword_in_comment")
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def test_lambda_handler(self):
        """assuming the tables have been created prior to testing"""
        event = {}
        context = {}

        lambda_handler(event, context)

        self.cursor.execute("SELECT * FROM Post")
        posts = self.cursor.fetchall()
        self.assertEqual(len(posts), 30)  # assuming data contains 30 posts

        self.cursor.execute("SELECT * FROM Comment")
        comments = self.cursor.fetchall()
        self.assertTrue(len(comments) > 0)


if __name__ == '__main__':
    unittest.main()
