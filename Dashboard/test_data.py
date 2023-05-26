from data import build_dataframe
import pandas.api.types as ptypes
DATAFRAME = build_dataframe()


def test_columns():
    """Test that correct column names are extracted from the Postgres DB into Pandas"""
    column_names = list(DATAFRAME.columns.values)
    assert len(column_names) == 10
    assert column_names == ['comment_id', 'comment_time', 'comment', 'score',
                            'sentiment', 'post_id', 'comment_keyword', 'post_keyword', 'post_time', 'title']


def test_non_empty():
    """Test that data has actually been pulled in from the database."""
    assert len(DATAFRAME) > 0


def test_data_types():
    """Test that the data has been loaded in with the correct types"""
    assert all(ptypes.is_numeric_dtype(
        DATAFRAME[col]) for col in ['comment_id', 'score', 'post_id', 'sentiment'])
    assert all(ptypes.is_string_dtype(
        DATAFRAME[col]) for col in ['comment', 'comment_keyword', 'post_keyword', 'title'])
    assert all(ptypes.is_datetime64_any_dtype(
        DATAFRAME[col]) for col in ['post_time', 'comment_time'])
