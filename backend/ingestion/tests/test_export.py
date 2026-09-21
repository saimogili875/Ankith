import pytest
from ingestion.management.commands.export_videos import parse_iso8601_duration

def test_parse_iso8601_duration():
    assert parse_iso8601_duration('PT1M30S') == 90
    assert parse_iso8601_duration('PT1H2M3S') == 3723
    assert parse_iso8601_duration('PT45S') == 45
    assert parse_iso8601_duration('PT2H') == 7200
    assert parse_iso8601_duration('') == 0
    assert parse_iso8601_duration(None) == 0

def test_short_duration_threshold():
    assert parse_iso8601_duration('PT3M') <= 180
    assert parse_iso8601_duration('PT3M1S') > 180
