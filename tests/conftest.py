"""Shared test configuration and fixtures."""

import pytest
import sys
import os

# Add the app directory to the Python path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    os.environ.setdefault('ENV', 'development')
    os.environ.setdefault('AMAZON_ACCESS_KEY', 'test_access_key')
    os.environ.setdefault('AMAZON_SECRET_KEY', 'test_secret_key')
    os.environ.setdefault('AMAZON_PARTNER_TAG', 'test_partner_tag')
    os.environ.setdefault('AMAZON_MARKETPLACE', 'test_marketplace')
    os.environ.setdefault('AMAZON_HOST', 'test_host')
    os.environ.setdefault('AMAZON_REGION', 'test_region')
