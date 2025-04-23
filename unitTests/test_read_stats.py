import pytest
import logging
from unittest.mock import MagicMock
from ppModule.binFiles.read_stats import ReadStats
from ppModule.utils.stats_reader import StatsReader

# filepath: ppModule/binFiles/test_read_stats.py

def test_stats_orienter_valid_case(monkeypatch):
    """Test stats_orienter with a valid case."""
    # Mock the StatsReader class to include a method for the case
    mock_method = MagicMock()
    monkeypatch.setattr(StatsReader, "stats_stbl", mock_method)

def test_stats_orienter_invalid_case_logs_error(monkeypatch, caplog):
    """Test stats_orienter logs an error for an invalid case."""
    # Mock the StatsReader class to include a default method
    mock_default_method = MagicMock()
    monkeypatch.setattr(StatsReader, "stats_stbl", mock_default_method)
    # Create an instance of ReadStats with an invalid case
    read_stats = ReadStats(directory="mock_dir", case="invalid_case", info={})
    # Call stats_orienter and capture logs
    with caplog.at_level(logging.ERROR):
        result = read_stats.stats_orienter()
    # Assert that the default method is returned
    assert result == mock_default_method
    # Assert that the error message is logged
    assert "Method stats_invalid_case not found in StatsReader class" in caplog.text

def test_stats_orienter_valid_case_logs_no_error(monkeypatch, caplog):
    """Test stats_orienter does not log an error for a valid case."""
    # Mock the StatsReader class to include a method for the case
    mock_method = MagicMock()
    monkeypatch.setattr(StatsReader, "stats_stbl", mock_method)
    # Create an instance of ReadStats with a valid case
    read_stats = ReadStats(directory="mock_dir", case="stbl", info={})
    # Call stats_orienter and capture logs
    with caplog.at_level(logging.ERROR):
        result = read_stats.stats_orienter()
    # Assert that the correct method is returned
    assert result == mock_method
    # Assert that no error message is logged
    assert "Method stats_stbl not found in StatsReader class" not in caplog.text

def test_stats_orienter_empty_case_logs_error(monkeypatch, caplog):
    """Test stats_orienter logs an error for an empty case."""
    # Mock the StatsReader class to include a default method
    mock_default_method = MagicMock()
    monkeypatch.setattr(StatsReader, "stats_stbl", mock_default_method)
    # Create an instance of ReadStats with an empty case
    read_stats = ReadStats(directory="mock_dir", case="", info={})
    # Call stats_orienter and capture logs
    with caplog.at_level(logging.ERROR):
        result = read_stats.stats_orienter()
    # Assert that the default method is returned
    assert result == mock_default_method
    # Assert that the error message is logged
    assert "Method stats_ not found in StatsReader class" in caplog.text

def test_stats_orienter_case_insensitivity_logs_no_error(monkeypatch, caplog):
    """Test stats_orienter does not log an error for case-insensitive input."""
    # Mock the StatsReader class to include a method for the case
    mock_method = MagicMock()
    monkeypatch.setattr(StatsReader, "stats_stbl", mock_method)
    # Create an instance of ReadStats with a case in uppercase
    read_stats = ReadStats(directory="mock_dir", case="STBL", info={})
    # Call stats_orienter and capture logs
    with caplog.at_level(logging.ERROR):
        result = read_stats.stats_orienter()
    # Assert that the correct method is returned
    assert result == mock_method
    # Assert that no error message is logged
    assert "Method stats_STBL not found in StatsReader class" not in caplog.text
