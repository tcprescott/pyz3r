"""Tests for pyz3r.exceptions module."""

import pytest
from pyz3r import exceptions


class TestExceptions:
    """Test exception classes."""

    def test_pyz3r_exception(self):
        """Test base Pyz3rException."""
        exc = exceptions.Pyz3rException("Test message")
        assert str(exc) == "Test message"
        assert isinstance(exc, Exception)

    def test_alttpr_failed_to_retrieve(self):
        """Test AlttprFailedToRetrieve exception."""
        exc = exceptions.AlttprFailedToRetrieve("Failed to retrieve")
        assert str(exc) == "Failed to retrieve"
        assert isinstance(exc, exceptions.Pyz3rException)

    def test_alttpr_failed_to_generate(self):
        """Test AlttprFailedToGenerate exception."""
        exc = exceptions.AlttprFailedToGenerate("Failed to generate")
        assert str(exc) == "Failed to generate"
        assert isinstance(exc, exceptions.Pyz3rException)

    def test_unable_to_retrieve(self):
        """Test UnableToRetrieve exception."""
        exc = exceptions.UnableToRetrieve("Unable to retrieve")
        assert str(exc) == "Unable to retrieve"
        assert isinstance(exc, exceptions.Pyz3rException)

    def test_unable_to_generate(self):
        """Test UnableToGenerate exception."""
        exc = exceptions.UnableToGenerate("Unable to generate")
        assert str(exc) == "Unable to generate"
        assert isinstance(exc, exceptions.Pyz3rException)

    def test_exception_inheritance(self):
        """Test that all custom exceptions inherit from Pyz3rException."""
        assert issubclass(exceptions.AlttprFailedToRetrieve, exceptions.Pyz3rException)
        assert issubclass(exceptions.AlttprFailedToGenerate, exceptions.Pyz3rException)
        assert issubclass(exceptions.UnableToRetrieve, exceptions.Pyz3rException)
        assert issubclass(exceptions.UnableToGenerate, exceptions.Pyz3rException)
