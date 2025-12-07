"""Tests for import_service.py"""
import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.import_service import ImportService


def test_import_service_exists():
    """Test that ImportService has process_import_job static method"""
    assert hasattr(ImportService, 'process_import_job')
    assert callable(getattr(ImportService, 'process_import_job'))


# Note: Full testing of process_import_job would require mocking SessionLocal, 
# asyncio, and external API calls. These are better tested as integration tests
# through the job controller endpoints.
