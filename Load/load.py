"""Script to load the data into the tables created in the
create_tables.sql file"""
import os
import json
import psycopg2
import boto3
from dotenv import load_dotenv

load_dotenv()

DB_HOST=os.environ.get('DB_HOST')
DB_PORT=os.environ.get('DB_PORT')
DB_NAME=os.environ.get('DB_NAME')
DB_USER=os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
FILE_NAME = "posts_data.json"

print(DB_HOST, DB_PORT, DB_NAME, DB_USER)

def lambda_handler(event, context):
    # Establish database connection
    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = connection.cursor()
    cursor.execute(open("/var/task/create_tables.sql", "r").read())
    s3 = boto3.resource(service_name='s3', region_name=os.environ.get("region_name"),
                        aws_access_key_id=os.environ.get("access_key"),aws_secret_access_key=os.environ.get("secret_access_key"))
    bucket_name = os.environ.get("bucket_name")
    s3.Bucket(bucket_name).download_file(FILE_NAME, f'/tmp/{FILE_NAME}')


    with open(f'/tmp/{FILE_NAME}') as file:
        data = json.loads(file.read())

    # Process each post in the json input
    for post in data:
        # Check if post exists in the database based on title
        cursor.execute(
            "SELECT post_id FROM Post WHERE title = %s", (post['title'],))
        post_id = cursor.fetchone()

        if not post_id:
            # Insert the new post into the database
            cursor.execute("INSERT INTO Post (post_time, title) VALUES (%s, %s) RETURNING post_id",
                           (post['datetime'], post['title']))
            post_id = cursor.fetchone()[0]

            # Insert keywords associated with the post
            for keyword in post['keywords']:
                if len(keyword) > 50:
                    continue
                cursor.execute(
                    "SELECT post_keyword_id FROM Post_keyword WHERE post_keyword = %s", (keyword,))
                keyword_id = cursor.fetchone()

                if not keyword_id:
                    # Insert new keyword into the database
                    cursor.execute("INSERT INTO Post_keyword (post_keyword) VALUES (%s) RETURNING post_keyword_id",
                                   (keyword,))
                    keyword_id = cursor.fetchone()[0]

                # Insert the relationship between post and keyword
                cursor.execute("INSERT INTO Keyword_in_post (post_id, post_keyword_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                               (post_id, keyword_id))

        # Process comments
        for comment in post['comments']:
            # Check if comment exists in the database based on comment text
            cursor.execute(
                "SELECT comment_id FROM Comment WHERE comment = %s", (comment['comment'],))
            comment_id = cursor.fetchone()

            if comment_id:
                continue  # Skip this comment if it already exists

            # Insert the new comment into the database
            cursor.execute("INSERT INTO Comment (comment_time, comment, score, sentiment, post_id) VALUES (%s, %s, %s, %s, %s) RETURNING comment_id",
                           (comment['datetime'], comment['comment'], comment['score'], comment['sentiment']['compound'], post_id))
            comment_id = cursor.fetchone()[0]

            # Insert keywords associated with the comment
            for keyword in comment['keywords']:
                if len(keyword) > 50:
                    continue
                cursor.execute(
                    "SELECT comment_keyword_id FROM Comment_keyword WHERE comment_keyword = %s", (keyword,))
                keyword_id = cursor.fetchone()

                if not keyword_id:
                    # Insert new keyword into the database
                    cursor.execute("INSERT INTO Comment_keyword (comment_keyword) VALUES (%s) RETURNING comment_keyword_id",
                                   (keyword,))
                    keyword_id = cursor.fetchone()[0]

                # Insert the relationship between comment and keyword
                cursor.execute("INSERT INTO Keyword_in_comment (comment_id, comment_keyword_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                               (comment_id, keyword_id))

    # Commit the changes and close the connection
    connection.commit()
    cursor.close()
    connection.close()



    return "Data processed successfully"

