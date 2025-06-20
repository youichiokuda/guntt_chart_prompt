import pandas as pd
from app import is_json_like, json_to_df


def test_is_json_like_valid():
    assert is_json_like('{"a": 1}')
    assert is_json_like('[1, 2, 3]')
    assert is_json_like(' [ {"a": 1} ] ')


def test_is_json_like_invalid():
    assert not is_json_like('Just a string')
    assert not is_json_like('1, 2, 3')
    assert not is_json_like('some {text')


def test_json_to_df_parsing():
    json_input = '[{"task": "task1", "start": "2024-01-01", "end": "2024-01-05"}, {"task": "task2", "start": "2024-01-06", "end": "2024-01-10"}]'
    df = json_to_df(json_input)
    assert list(df.columns) == ["task", "start", "end"]
    assert len(df) == 2
    assert pd.api.types.is_datetime64_any_dtype(df["start"])
    assert pd.api.types.is_datetime64_any_dtype(df["end"])
    assert df.iloc[0]["task"] == "task1"
    assert df.iloc[0]["start"] == pd.Timestamp("2024-01-01")

