"""Module for data extraction and loading into a Pandas dataframe used for visualisation."""
import os
import pandas as pd
from pandas import DataFrame
from sqlalchemy import URL, create_engine


def build_dataframe() -> DataFrame:
    """Build a dataframe based on the contents of a postgres database and returns them clean."""
    url_object = URL.create(
        "postgresql+psycopg2",
        username=os.environ.get('USERNAME'),
        password=os.environ.get('PASSWORD'),
        host=os.environ.get('HOST'),
        database=os.environ.get('DATABASE')
    )
    engine = create_engine(url_object)

    post = pd.read_sql_table(table_name='post', con=engine)
    post_keyword = pd.read_sql_table(table_name='post_keyword', con=engine)
    keyword_in_post = pd.read_sql_table(
        table_name='keyword_in_post', con=engine)
    comment = pd.read_sql_table(table_name='comment', con=engine)
    comment_keyword = pd.read_sql_table(
        table_name='comment_keyword', con=engine)
    keyword_in_comment = pd.read_sql_table(
        table_name='keyword_in_comment', con=engine)

    post_keywords = pd.merge(post_keyword, keyword_in_post, how='inner',
                             left_on='post_keyword_id',
                            right_on='post_keyword_id').drop('post_keyword_id', axis=1)
    posts_and_keywords = pd.merge(
        post_keywords, post, how='inner', left_on='post_id', right_on='post_id')

    comment_keywords = pd.merge(comment_keyword, keyword_in_comment, how='inner',
                                left_on='comment_keyword_id', right_on='comment_keyword_id')
    comments_and_keywords = pd.merge(comment, comment_keywords, how='inner',
                                     left_on='comment_id',
                                    right_on='comment_id').drop('comment_keyword_id', axis=1)

    return pd.merge(comments_and_keywords, posts_and_keywords, how='inner', on='post_id')
