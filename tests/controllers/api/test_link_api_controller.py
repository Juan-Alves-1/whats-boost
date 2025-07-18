"""Tests for the link API controller."""

import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.controllers.api.link_api_controller import link, LinkInput, LinkOutput
from app.repositories.product import ProductNotFound, ProductRepositoryError
from app.repositories.openai import (
    OpenAIAPIError,
    OpenAIRateLimitError,
    OpenAIRepositoryError,
)
from app.schemas.product import Product


class TestLinkAPIController:
    """Test suite for link API controller."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock authenticated user."""
        return {"email": "test@example.com", "id": "123"}

    @pytest.fixture
    def sample_product(self):
        """Create a sample product for testing."""
        return Product(
            title="Test Product",
            price="$29.99",
            old_price="$39.99",
            image="https://example.com/image.jpg",
            url="https://amazon.com/dp/B123456789"
        )

    def test_link_input_schema(self):
        """Test LinkInput schema validation."""

        valid_input = LinkInput(url="https://amazon.com/dp/B123456789")
        assert str(valid_input.url) == "https://amazon.com/dp/B123456789"

        with pytest.raises(ValueError):
            LinkInput(url="invalid-url")

    def test_link_output_schema(self):
        """Test LinkOutput schema."""
        output = LinkOutput(
            image="https://example.com/image.jpg",
            message="Check out this amazing product!"
        )
        assert output.image == "https://example.com/image.jpg"
        assert output.message == "Check out this amazing product!"

    @patch('app.controllers.api.link_api_controller.product_repository')
    @patch('app.controllers.api.link_api_controller.openai_repository')
    @pytest.mark.asyncio
    async def test_link_success(
        self,
        mock_openai_repo,
        mock_product_repo,
        mock_user,
        sample_product
    ):
        """Test successful link message generation."""

        mock_product_repo.get_product_by_url.return_value = sample_product
        mock_openai_repo.generate_promotional_message.return_value = "Amazing product message!"

        input_data = LinkInput(url="https://amazon.com/dp/B123456789")

        result = await link(input_data, mock_user)

        assert isinstance(result, LinkOutput)
        assert result.image == sample_product.image
        assert result.message == "Amazing product message!"

        mock_product_repo.get_product_by_url.assert_called_once_with(
            "https://amazon.com/dp/B123456789"
        )
        mock_openai_repo.generate_promotional_message.assert_called_once_with(
            sample_product
        )

    @patch('app.controllers.api.link_api_controller.product_repository')
    @pytest.mark.asyncio
    async def test_link_product_not_found(
        self,
        mock_product_repo,
        mock_user
    ):
        """Test handling when product is not found."""

        mock_product_repo.get_product_by_url.side_effect = ProductNotFound(
            "https://amazon.com/dp/B123456789"
        )

        input_data = LinkInput(url="https://amazon.com/dp/B123456789")

        with pytest.raises(HTTPException) as exc_info:
            await link(input_data, mock_user)

        assert exc_info.value.status_code == 404
        assert "Product not found" in str(exc_info.value.detail)

    @patch('app.controllers.api.link_api_controller.product_repository')
    @pytest.mark.asyncio
    async def test_link_product_repository_error(
        self,
        mock_product_repo,
        mock_user
    ):
        """Test handling of ProductRepositoryError."""

        mock_product_repo.get_product_by_url.side_effect = ProductRepositoryError(
            "Error"
        )

        input_data = LinkInput(url="https://amazon.com/dp/B123456789")

        with pytest.raises(HTTPException) as exc_info:
            await link(input_data, mock_user)

        assert exc_info.value.status_code == 500
        assert "Error" in str(exc_info.value.detail)

    @patch('app.controllers.api.link_api_controller.product_repository')
    @patch('app.controllers.api.link_api_controller.openai_repository')
    @pytest.mark.asyncio
    async def test_link_openai_rate_limit_error(
        self,
        mock_openai_repo,
        mock_product_repo,
        mock_user,
        sample_product
    ):
        """Test handling of OpenAI rate limit error."""

        mock_product_repo.get_product_by_url.return_value = sample_product
        mock_openai_repo.generate_promotional_message.side_effect = OpenAIRateLimitError()

        input_data = LinkInput(url="https://amazon.com/dp/B123456789")

        with pytest.raises(HTTPException) as exc_info:
            await link(input_data, mock_user)

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in str(exc_info.value.detail)

    @patch('app.controllers.api.link_api_controller.product_repository')
    @patch('app.controllers.api.link_api_controller.openai_repository')
    @pytest.mark.asyncio
    async def test_link_openai_api_error(
        self,
        mock_openai_repo,
        mock_product_repo,
        mock_user,
        sample_product
    ):
        """Test handling of OpenAI API error."""

        mock_product_repo.get_product_by_url.return_value = sample_product
        mock_openai_repo.generate_promotional_message.side_effect = OpenAIAPIError(
            "API key invalid"
        )

        input_data = LinkInput(url="https://amazon.com/dp/B123456789")

        with pytest.raises(HTTPException) as exc_info:
            await link(input_data, mock_user)

        assert exc_info.value.status_code == 502
        assert "error occurred while communicating with the OpenAI API" in str(exc_info.value.detail)

    @patch('app.controllers.api.link_api_controller.product_repository')
    @patch('app.controllers.api.link_api_controller.openai_repository')
    @pytest.mark.asyncio
    async def test_link_openai_repository_error(
        self,
        mock_openai_repo,
        mock_product_repo,
        mock_user,
        sample_product
    ):
        """Test handling of OpenAI repository error."""

        mock_product_repo.get_product_by_url.return_value = sample_product
        mock_openai_repo.generate_promotional_message.side_effect = OpenAIRepositoryError(
            "Internal repository error"
        )

        input_data = LinkInput(url="https://amazon.com/dp/B123456789")

        with pytest.raises(HTTPException) as exc_info:
            await link(input_data, mock_user)

        assert exc_info.value.status_code == 500
        assert "internal error occurred" in str(exc_info.value.detail)

    @patch('app.controllers.api.link_api_controller.product_repository')
    @patch('app.controllers.api.link_api_controller.openai_repository')
    @pytest.mark.asyncio
    async def test_url_conversion_to_string(
        self,
        mock_openai_repo,
        mock_product_repo,
        mock_user,
        sample_product
    ):
        """Test that URL is properly converted to string when passed to repository."""

        mock_product_repo.get_product_by_url.return_value = sample_product
        mock_openai_repo.generate_promotional_message.return_value = "Test message"

        test_url = "https://amazon.com/dp/B123456789"
        input_data = LinkInput(url=test_url)

        result = await link(input_data, mock_user)

        mock_product_repo.get_product_by_url.assert_called_once_with(test_url)
        assert result.message == "Test message"

    def test_link_input_accepts_various_url_formats(self):
        """Test that LinkInput accepts various valid URL formats."""

        valid_urls = [
            "https://amazon.com/dp/B123456789",
            "https://www.amazon.com/product/B987654321",
            "http://amazon.com/item/123",
            "https://amazon.co.uk/dp/B111111111"
        ]

        for url in valid_urls:
            input_data = LinkInput(url=url)
            assert str(input_data.url) == url

    def test_link_input_rejects_invalid_urls(self):
        """Test that LinkInput rejects invalid URLs."""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",  # Valid URL but not HTTP/HTTPS
            "",
            "just-text",
            "http://",
            "://missing-scheme"
        ]

        for url in invalid_urls:
            with pytest.raises(ValueError):
                LinkInput(url=url)

    @patch('app.controllers.api.link_api_controller.product_repository')
    @patch('app.controllers.api.link_api_controller.openai_repository')
    @pytest.mark.asyncio
    async def test_link_with_product_without_old_price(
        self,
        mock_openai_repo,
        mock_product_repo,
        mock_user
    ):
        """Test successful link message generation with product that has no old price."""

        product_no_old_price = Product(
            title="Test Product",
            price="$29.99",
            old_price=None,
            image="https://example.com/image.jpg",
            url="https://amazon.com/dp/B123456789"
        )

        mock_product_repo.get_product_by_url.return_value = product_no_old_price
        mock_openai_repo.generate_promotional_message.return_value = "Great product!"

        input_data = LinkInput(url="https://amazon.com/dp/B123456789")

        result = await link(input_data, mock_user)

        assert isinstance(result, LinkOutput)
        assert result.image == product_no_old_price.image
        assert result.message == "Great product!"

    @patch('app.controllers.api.link_api_controller.product_repository')
    @pytest.mark.asyncio
    async def test_link_handles_unexpected_exceptions(
        self,
        mock_product_repo,
        mock_user
    ):
        """Test handling of unexpected exceptions."""

        mock_product_repo.get_product_by_url.side_effect = Exception("Unexpected error")

        input_data = LinkInput(url="https://amazon.com/dp/B123456789")

        with pytest.raises(Exception, match="Unexpected error"):
            await link(input_data, mock_user)
