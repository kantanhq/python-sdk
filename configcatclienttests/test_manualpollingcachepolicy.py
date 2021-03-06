import logging
import unittest
from requests import HTTPError

from configcatclient.configcache import InMemoryConfigCache
from configcatclient.manualpollingcachepolicy import ManualPollingCachePolicy
from configcatclienttests.mocks import (
    ConfigFetcherMock,
    ConfigFetcherWithErrorMock,
    TEST_JSON,
)

logging.basicConfig()


class ManualPollingCachePolicyTests(unittest.TestCase):
    def test_without_refresh(self):
        config_fetcher = ConfigFetcherMock()
        config_cache = InMemoryConfigCache()
        cache_policy = ManualPollingCachePolicy(config_fetcher, config_cache)
        value = cache_policy.get()
        self.assertEqual(value, None)
        self.assertEqual(config_fetcher.get_call_count, 0)
        cache_policy.stop()

    def test_with_refresh(self):
        config_fetcher = ConfigFetcherMock()
        config_cache = InMemoryConfigCache()
        cache_policy = ManualPollingCachePolicy(config_fetcher, config_cache)
        cache_policy.force_refresh()
        value = cache_policy.get()
        self.assertEqual(value, TEST_JSON)
        self.assertEqual(config_fetcher.get_call_count, 1)
        cache_policy.stop()

    def test_with_force_refresh(self):
        config_fetcher = ConfigFetcherMock()
        config_cache = InMemoryConfigCache()
        cache_policy = ManualPollingCachePolicy(config_fetcher, config_cache)
        cache_policy.force_refresh()
        value = cache_policy.get()
        self.assertEqual(value, TEST_JSON)
        self.assertEqual(config_fetcher.get_call_count, 1)

        try:
            # Clear the cache
            cache_policy._lock.acquire_write()
            cache_policy._config_cache.set(None)
        finally:
            cache_policy._lock.release_write()

        self.assertEqual(value, TEST_JSON)
        self.assertEqual(config_fetcher.get_call_count, 1)
        cache_policy.stop()

    def test_with_refresh_http_error(self):
        config_fetcher = ConfigFetcherWithErrorMock(HTTPError("error"))
        config_cache = InMemoryConfigCache()
        cache_policy = ManualPollingCachePolicy(config_fetcher, config_cache)
        cache_policy.force_refresh()
        value = cache_policy.get()
        self.assertEqual(value, None)
        cache_policy.stop()

    def test_with_refresh_exception(self):
        config_fetcher = ConfigFetcherWithErrorMock(Exception("error"))
        config_cache = InMemoryConfigCache()
        cache_policy = ManualPollingCachePolicy(config_fetcher, config_cache)
        cache_policy.force_refresh()
        value = cache_policy.get()
        self.assertEqual(value, None)
        cache_policy.stop()


if __name__ == "__main__":
    unittest.main()
