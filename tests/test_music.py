# tests/test_music.py
import pytest
from server.music import MusicQueryProcessor

def test_sql_generation(db):
    """Test SQL query generation"""
    processor = MusicQueryProcessor()
    query = "Find albums by Beatles"
    sql = processor.generate_sql(query)
    assert 'SELECT' in sql.upper()
    assert 'FROM music' in sql.lower()
    assert 'beatles' in sql.lower()

def test_sql_validation(db):
    """Test SQL query validation"""
    processor = MusicQueryProcessor()
    with pytest.raises(Exception):
        processor._validate_and_clean_sql("DROP TABLE music")
