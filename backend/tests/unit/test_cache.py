"""Unit tests for cache manager"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.cache.redis_manager import CacheManager, cache_result
import json


class TestCacheManager:
    """Test CacheManager class"""

    def test_init_without_redis(self):
        """Test initialization without Redis"""
        with patch.dict('os.environ', {}, clear=True):
            cache = CacheManager()
            assert not cache.is_enabled

    def test_init_with_redis_unavailable(self):
        """Test initialization when Redis library is not available"""
        with patch('app.cache.redis_manager.REDIS_AVAILABLE', False):
            cache = CacheManager(redis_url="redis://localhost:6379")
            assert not cache.is_enabled

    @patch('app.cache.redis_manager.redis')
    def test_init_with_redis_connection_error(self, mock_redis):
        """Test initialization when Redis connection fails"""
        mock_client = Mock()
        mock_client.ping.side_effect = Exception("Connection failed")
        mock_redis.from_url.return_value = mock_client

        cache = CacheManager(redis_url="redis://localhost:6379")
        assert not cache.is_enabled

    @patch('app.cache.redis_manager.redis')
    def test_init_with_redis_success(self, mock_redis):
        """Test successful initialization with Redis"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.from_url.return_value = mock_client

        cache = CacheManager(redis_url="redis://localhost:6379")
        assert cache.is_enabled

    def test_get_when_disabled(self):
        """Test get when cache is disabled"""
        cache = CacheManager()
        result = cache.get("test_key")
        assert result is None

    @patch('app.cache.redis_manager.redis')
    def test_get_success(self, mock_redis):
        """Test successful get operation"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.get.return_value = json.dumps({"data": "test"})
        mock_redis.from_url.return_value = mock_client

        cache = CacheManager(redis_url="redis://localhost:6379")
        result = cache.get("test_key")
        assert result == {"data": "test"}

    @patch('app.cache.redis_manager.redis')
    def test_get_string_value(self, mock_redis):
        """Test get operation with string value"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.get.return_value = "simple_string"
        mock_redis.from_url.return_value = mock_client

        cache = CacheManager(redis_url="redis://localhost:6379")
        result = cache.get("test_key")
        assert result == "simple_string"

    @patch('app.cache.redis_manager.redis')
    def test_get_not_found(self, mock_redis):
        """Test get operation when key doesn't exist"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.get.return_value = None
        mock_redis.from_url.return_value = mock_client

        cache = CacheManager(redis_url="redis://localhost:6379")
        result = cache.get("nonexistent_key")
        assert result is None

    @patch('app.cache.redis_manager.redis')
    def test_get_error(self, mock_redis):
        """Test get operation with Redis error"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.get.side_effect = Exception("Redis error")
        mock_redis.from_url.return_value = mock_client

        cache = CacheManager(redis_url="redis://localhost:6379")
        result = cache.get("test_key")
        assert result is None

    def test_set_when_disabled(self):
        """Test set when cache is disabled"""
        cache = CacheManager()
        result = cache.set("test_key", "test_value")
        assert result is False

    @patch('app.cache.redis_manager.redis')
    def test_set_success(self, mock_redis):
        """Test successful set operation"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.from_url.return_value = mock_client

        cache = CacheManager(redis_url="redis://localhost:6379")
        result = cache.set("test_key", {"data": "test"}, ttl=300)
        assert result is True
        mock_client.setex.assert_called_once()

    @patch('app.cache.redis_manager.redis')
    def test_set_with_default_ttl(self, mock_redis):
        """Test set operation with default TTL"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.from_url.return_value = mock_client

        cache = CacheManager(redis_url="redis://localhost:6379", default_ttl=7200)
        result = cache.set("test_key", "test_value")
        assert result is True
        # Verify it used default TTL
        call_args = mock_client.setex.call_args
        assert call_args[0][1] == 7200  # TTL argument

    @patch('app.cache.redis_manager.redis')
    def test_set_error(self, mock_redis):
        """Test set operation with Redis error"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.setex.side_effect = Exception("Redis error")
        mock_redis.from_url.return_value = mock_client

        cache = CacheManager(redis_url="redis://localhost:6379")
        result = cache.set("test_key", "test_value")
        assert result is False

    def test_delete_when_disabled(self):
        """Test delete when cache is disabled"""
        cache = CacheManager()
        result = cache.delete("test_key")
        assert result is False

    @patch('app.cache.redis_manager.redis')
    def test_delete_success(self, mock_redis):
        """Test successful delete operation"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.from_url.return_value = mock_client

        cache = CacheManager(redis_url="redis://localhost:6379")
        result = cache.delete("test_key")
        assert result is True
        mock_client.delete.assert_called_once_with("test_key")

    @patch('app.cache.redis_manager.redis')
    def test_delete_error(self, mock_redis):
        """Test delete operation with Redis error"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.delete.side_effect = Exception("Redis error")
        mock_redis.from_url.return_value = mock_client

        cache = CacheManager(redis_url="redis://localhost:6379")
        result = cache.delete("test_key")
        assert result is False

    def test_exists_when_disabled(self):
        """Test exists when cache is disabled"""
        cache = CacheManager()
        result = cache.exists("test_key")
        assert result is False

    @patch('app.cache.redis_manager.redis')
    def test_exists_true(self, mock_redis):
        """Test exists returns True for existing key"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.exists.return_value = 1
        mock_redis.from_url.return_value = mock_client

        cache = CacheManager(redis_url="redis://localhost:6379")
        result = cache.exists("test_key")
        assert result is True

    @patch('app.cache.redis_manager.redis')
    def test_exists_false(self, mock_redis):
        """Test exists returns False for non-existing key"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.exists.return_value = 0
        mock_redis.from_url.return_value = mock_client

        cache = CacheManager(redis_url="redis://localhost:6379")
        result = cache.exists("test_key")
        assert result is False

    def test_clear_when_disabled(self):
        """Test clear when cache is disabled"""
        cache = CacheManager()
        result = cache.clear()
        assert result is False

    @patch('app.cache.redis_manager.redis')
    def test_clear_success(self, mock_redis):
        """Test successful clear operation"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.keys.return_value = ["key1", "key2", "key3"]
        mock_redis.from_url.return_value = mock_client

        cache = CacheManager(redis_url="redis://localhost:6379")
        result = cache.clear("test:*")
        assert result is True
        mock_client.delete.assert_called_once_with("key1", "key2", "key3")

    @patch('app.cache.redis_manager.redis')
    def test_clear_no_keys(self, mock_redis):
        """Test clear when no keys match pattern"""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_client.keys.return_value = []
        mock_redis.from_url.return_value = mock_client

        cache = CacheManager(redis_url="redis://localhost:6379")
        result = cache.clear("test:*")
        assert result is True
        mock_client.delete.assert_not_called()


class TestCacheDecorator:
    """Test cache_result decorator"""

    @pytest.mark.asyncio
    async def test_async_cache_miss(self):
        """Test async function cache miss"""
        call_count = 0

        @cache_result("test", ttl=300)
        async def test_func(value: str):
            nonlocal call_count
            call_count += 1
            return f"result_{value}"

        # Mock cache manager to return None (cache miss)
        with patch('app.cache.redis_manager.get_cache_manager') as mock_get_cache:
            mock_cache = Mock()
            mock_cache.get.return_value = None
            mock_get_cache.return_value = mock_cache

            result = await test_func("test")
            assert result == "result_test"
            assert call_count == 1
            mock_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_cache_hit(self):
        """Test async function cache hit"""
        call_count = 0

        @cache_result("test", ttl=300)
        async def test_func(value: str):
            nonlocal call_count
            call_count += 1
            return f"result_{value}"

        # Mock cache manager to return cached value
        with patch('app.cache.redis_manager.get_cache_manager') as mock_get_cache:
            mock_cache = Mock()
            mock_cache.get.return_value = "cached_result"
            mock_get_cache.return_value = mock_cache

            result = await test_func("test")
            assert result == "cached_result"
            assert call_count == 0  # Function not called
            mock_cache.set.assert_not_called()

    def test_sync_cache_miss(self):
        """Test sync function cache miss"""
        call_count = 0

        @cache_result("test", ttl=300)
        def test_func(value: str):
            nonlocal call_count
            call_count += 1
            return f"result_{value}"

        # Mock cache manager to return None (cache miss)
        with patch('app.cache.redis_manager.get_cache_manager') as mock_get_cache:
            mock_cache = Mock()
            mock_cache.get.return_value = None
            mock_get_cache.return_value = mock_cache

            result = test_func("test")
            assert result == "result_test"
            assert call_count == 1
            mock_cache.set.assert_called_once()

    def test_sync_cache_hit(self):
        """Test sync function cache hit"""
        call_count = 0

        @cache_result("test", ttl=300)
        def test_func(value: str):
            nonlocal call_count
            call_count += 1
            return f"result_{value}"

        # Mock cache manager to return cached value
        with patch('app.cache.redis_manager.get_cache_manager') as mock_get_cache:
            mock_cache = Mock()
            mock_cache.get.return_value = "cached_result"
            mock_get_cache.return_value = mock_cache

            result = test_func("test")
            assert result == "cached_result"
            assert call_count == 0  # Function not called
            mock_cache.set.assert_not_called()

    def test_custom_key_builder(self):
        """Test decorator with custom key builder"""
        @cache_result("test", key_builder=lambda x, y: f"{x}:{y}")
        def test_func(x: int, y: int):
            return x + y

        with patch('app.cache.redis_manager.get_cache_manager') as mock_get_cache:
            mock_cache = Mock()
            mock_cache.get.return_value = None
            mock_get_cache.return_value = mock_cache

            test_func(5, 10)

            # Verify cache key was built with custom builder
            get_call_args = mock_cache.get.call_args[0]
            assert get_call_args[0] == "test:5:10"
