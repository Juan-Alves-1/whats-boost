import pytest

from unittest.mock import Mock, patch, MagicMock

from app.repositories.product import (
    ProductRepository,
    ProductRepositoryError,
)
from app.schemas.product import Product
from app.config.settings import Settings


class TestProductRepository:
    """Test suite for ProductRepository class."""

    @pytest.fixture
    def mock_settings(self):
        """Create a mock settings object for testing."""
        settings = Mock(spec=Settings)
        settings.AMAZON_ACCESS_KEY = "test_access_key"
        settings.AMAZON_SECRET_KEY = "test_secret_key"
        settings.AMAZON_PARTNER_TAG = "test_partner_tag"
        settings.AMAZON_MARKETPLACE = "test_marketplace"
        settings.AMAZON_HOST = "test_host"
        settings.AMAZON_REGION = "test_region"

        return settings

    @pytest.fixture
    def mock_amazon_api(self):
        """Create a mock Amazon API instance."""
        return Mock()

    @pytest.fixture
    def product_repository(self, mock_settings, mock_amazon_api):
        """Create a ProductRepository instance with mocked dependencies."""
        with patch('app.repositories.product.DefaultApi', return_value=mock_amazon_api):
            repo = ProductRepository(mock_settings)
            repo.amazon_api = mock_amazon_api
            return repo

    def test_init_creates_amazon_api_with_correct_parameters(self, mock_settings):
        """Test that the constructor initializes the Amazon API with correct parameters."""
        with patch('app.repositories.product.DefaultApi') as mock_api:
            ProductRepository(mock_settings)
            
            mock_api.assert_called_once_with(
                access_key=mock_settings.AMAZON_ACCESS_KEY,
                secret_key=mock_settings.AMAZON_SECRET_KEY,
                host=mock_settings.AMAZON_HOST,
                region=mock_settings.AMAZON_REGION,
            )

    def test_extract_asin_with_valid_url(self):
        """Test ASIN extraction with various valid Amazon URLs."""
        test_cases = [
            ("https://www.amazon.com/dp/B08N5WRWNW/", "B08N5WRWNW"),
            ("https://amazon.com/product/B123456789", "B123456789"),
            ("https://www.amazon.com/gp/product/B987654321/ref=something", "B987654321"),
            ("https://smile.amazon.com/dp/B111222333?tag=sometag", "B111222333"),
            ("https://www.amazon.com/Some-Product-Title/dp/B444555666/", "B444555666"),
        ]
        
        for url, expected_asin in test_cases:
            asin = ProductRepository._extract_asin(url)
            assert asin == expected_asin, f"Failed for URL: {url}"

    def test_extract_asin_with_invalid_url(self):
        """Test ASIN extraction with invalid URLs."""
        invalid_urls = [
            "https://www.google.com",
            "https://www.amazon.com/invalid",
            "https://www.amazon.com/dp/B12345",      # Too short
            "https://www.amazon.com/dp/B123456789X", # Too long
            "",
            "not-a-url",
        ]
        
        for url in invalid_urls:
            with pytest.raises(ProductRepositoryError, match="Could not extract ASIN from URL"):
                ProductRepository._extract_asin(url)

    @patch('app.repositories.product.create_amazon_shortlink')
    def test_get_product_by_url_success(self, mock_shortlink, product_repository):
        """Test successful product retrieval."""
        mock_shortlink.return_value = "https://short.url/test"
        
        mock_response = Mock()
        mock_item = Mock()
        
        mock_item.images.primary.large.url = "https://example.com/image.jpg"
        mock_item.item_info.title.display_value = "Test Product"
        mock_item.detail_page_url = "https://amazon.com/dp/B123456789"
        
        # TODO: Use real product's structure to test it better.
        mock_listing = {
            'Price': {
                'Money': {
                    'DisplayAmount': '$29.99'
                },
                'SavingBasis': {
                    'Money': {
                        'DisplayAmount': '$39.99'
                    }
                }
            }
        }
        mock_item.offers_v2.listings = [mock_listing]
        
        mock_response.items_result.items = [mock_item]
        product_repository.amazon_api.get_items.return_value = mock_response
        
        url = "https://amazon.com/dp/B123456789"
        result = product_repository.get_product_by_url(url)
        
        assert isinstance(result, Product)
        assert result.image == "https://example.com/image.jpg"
        assert result.title == "Test Product"
        assert result.url == "https://short.url/test"
        assert result.price == "$29.99"
        assert result.old_price == "$39.99"
        
        mock_shortlink.assert_called_once_with("Test Product", "https://amazon.com/dp/B123456789")

    @patch('app.repositories.product.create_amazon_shortlink')
    def test_get_product_by_url_success_no_saving_basis(self, mock_shortlink, product_repository):
        """Test successful product retrieval without saving basis (no old price)."""
        mock_shortlink.return_value = "https://short.url/test"
        
        mock_response = Mock()
        mock_item = Mock()
        
        mock_item.images.primary.large.url = "https://example.com/image.jpg"
        mock_item.item_info.title.display_value = "Test Product"
        mock_item.detail_page_url = "https://amazon.com/dp/B123456789"
        
        mock_listing = {
            'Price': {
                'Money': {
                    'DisplayAmount': '$29.99'
                }
            }
        }
        mock_item.offers_v2.listings = [mock_listing]
        
        mock_response.items_result.items = [mock_item]
        product_repository.amazon_api.get_items.return_value = mock_response
        
        url = "https://amazon.com/dp/B123456789"
        result = product_repository.get_product_by_url(url)
        
        assert isinstance(result, Product)
        assert result.old_price is None

    @patch('app.repositories.product.create_amazon_shortlink')
    def test_get_items_request_parameters(self, mock_shortlink, product_repository, mock_settings):
        """Test that GetItemsRequest is created with correct parameters."""
        mock_shortlink.return_value = "https://short.url/test"
        
        mock_response = Mock()
        mock_item = Mock()
        mock_item.images.primary.large.url = "https://example.com/image.jpg"
        mock_item.item_info.title.display_value = "Test Product"
        mock_item.detail_page_url = "https://amazon.com/dp/B123456789"
        mock_item.offers_v2.listings = [{'Price': {'Money': {'DisplayAmount': '$29.99'}}}]
        mock_response.items_result.items = [mock_item]
        
        product_repository.amazon_api.get_items.return_value = mock_response
        
        url = "https://amazon.com/dp/B123456789"
        product_repository.get_product_by_url(url)
        
        product_repository.amazon_api.get_items.assert_called_once()
        
        call_args = product_repository.amazon_api.get_items.call_args[0][0]
        
        assert call_args.partner_tag == mock_settings.AMAZON_PARTNER_TAG
        assert call_args.marketplace == mock_settings.AMAZON_MARKETPLACE
        assert call_args.item_ids == ["B123456789"]
        assert len(call_args.resources) == 4

    def test_generate_promotional_message(self, product_repository):
        """Test promotional message generation for a product."""
        product = Product(
            image="https://example.com/image.jpg",
            title="Test Product",
            url="https://short.url/test",
            price="$29.99",
            old_price="$39.99"
        )
        
        message = product_repository.generate_promotional_message(product)
        
        expected_message = """Test Product

De: $39.99
Por: $29.99

Link direto da promo: https://short.url/test"""
        
        assert message == expected_message

    def test_generate_promotional_message_no_old_price(self, product_repository):
        """Test promotional message generation for a product without an old price."""
        product = Product(
            image="https://example.com/image.jpg",
            title="Test Product",
            url="https://short.url/test",
            price="$29.99",
            old_price=None
        )
        
        message = product_repository.generate_promotional_message(product)
        
        expected_message = """Test Product

Por: $29.99

Link direto da promo: https://short.url/test"""
        
        assert message == expected_message

