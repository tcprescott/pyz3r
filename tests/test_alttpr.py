"""Tests for pyz3r.alttpr module."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pyz3r.alttpr import ALTTPR
from pyz3r.exceptions import Pyz3rException, AlttprFailedToGenerate, AlttprFailedToRetrieve


class TestALTTPRInit:
    """Test ALTTPR initialization."""

    def test_init_default(self):
        """Test default initialization."""
        alttpr = ALTTPR()
        assert alttpr.baseurl == 'https://alttpr.com'
        assert alttpr.data is None
        assert alttpr.hash is None
        assert alttpr.settings is None
        assert alttpr.auth is None

    def test_init_with_baseurl(self):
        """Test initialization with custom base URL."""
        alttpr = ALTTPR(baseurl='https://custom.url')
        assert alttpr.baseurl == 'https://custom.url'

    def test_init_with_auth(self):
        """Test initialization with authentication."""
        alttpr = ALTTPR(username='testuser', password='testpass')
        assert alttpr.auth is not None
        assert alttpr.auth.login == 'testuser'

    def test_init_without_password(self):
        """Test initialization with username but no password."""
        alttpr = ALTTPR(username='testuser')
        assert alttpr.auth is None


class TestALTTPRProperties:
    """Test ALTTPR properties."""

    def test_url_property(self):
        """Test URL property."""
        alttpr = ALTTPR()
        alttpr.hash = 'testHash123'
        assert alttpr.url == 'https://alttpr.com/h/testHash123'

    def test_uri_method(self):
        """Test URI construction method."""
        alttpr = ALTTPR(baseurl='https://example.com')
        assert alttpr.uri('/test/path') == 'https://example.com/test/path'

    def test_code_property_without_data(self):
        """Test code property raises exception without data."""
        alttpr = ALTTPR()
        with pytest.raises(Pyz3rException, match='Please specify a seed'):
            _ = alttpr.code

    def test_code_property_with_data(self):
        """Test code property with game data."""
        alttpr = ALTTPR()
        # Mock data with patch information
        # Note: seek_patch_data needs properly formatted patch data
        alttpr.data = {
            'patch': [
                {'100': [0, 1, 2, 3, 4]},  # Some patch
                {'1573397': [0, 1, 2, 3, 4]}  # Code bytes: Bow, Boomerang, Hookshot, Bombs, Mushroom
            ]
        }
        code = alttpr.code
        assert isinstance(code, list)
        assert len(code) == 5
        assert code[0] == 'Bow'


@pytest.mark.asyncio
class TestALTTPRGenerate:
    """Test ALTTPR game generation (async tests)."""

    async def test_generate_success(self):
        """Test successful game generation."""
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={'hash': 'testHash', 'patch': []})
        
        with patch('aiohttp.request') as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            
            seed = await ALTTPR.generate(settings={'glitches': 'none'})
            
            assert seed.hash == 'testHash'
            assert seed.data['hash'] == 'testHash'

    async def test_generate_failure_after_retries(self):
        """Test generation failure after all retries."""
        import aiohttp
        
        with patch('aiohttp.request') as mock_request:
            # Simulate connection errors for all retry attempts
            mock_request.return_value.__aenter__.side_effect = aiohttp.client_exceptions.ServerDisconnectedError()
            
            with pytest.raises(AlttprFailedToGenerate):
                await ALTTPR.generate(settings={'glitches': 'none'})


@pytest.mark.asyncio
class TestALTTPRRetrieve:
    """Test ALTTPR game retrieval (async tests)."""

    async def test_retrieve_success(self):
        """Test successful game retrieval."""
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={'hash': 'testHash', 'patch': []})
        
        with patch('aiohttp.request') as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            
            seed = await ALTTPR.retrieve(hash_id='testHash')
            
            assert seed.hash == 'testHash'
            assert seed.data['hash'] == 'testHash'

    async def test_retrieve_failure_after_retries(self):
        """Test retrieval failure after all retries."""
        import aiohttp
        
        with patch('aiohttp.request') as mock_request:
            # Simulate connection errors for all retry attempts
            mock_request.return_value.__aenter__.side_effect = aiohttp.client_exceptions.ServerDisconnectedError()
            
            with pytest.raises(AlttprFailedToRetrieve):
                await ALTTPR.retrieve(hash_id='notFound')


class TestALTTPRFormatSpoiler:
    """Test spoiler formatting."""

    def test_get_formatted_spoiler_without_data(self):
        """Test formatted spoiler without game data."""
        alttpr = ALTTPR()
        alttpr.data = {
            'spoiler': {
                'meta': {
                    'spoilers': 'off'  # Spoilers disabled
                }
            }
        }
        result = alttpr.get_formatted_spoiler()
        # Should return None when spoilers are off
        assert result is None


class TestALTTPRBackwardsCompatibility:
    """Test backwards compatibility with old API."""

    def test_hash_vs_hash_id_attribute(self):
        """Test that both hash and hash_id work."""
        alttpr = ALTTPR()
        alttpr.hash = 'test123'
        # Both should work
        assert alttpr.hash == 'test123'
        assert hasattr(alttpr, 'hash_id')
