import re
import httpx
from app.config import settings
from app.schemas.product import Product

from app.utils.logger import logger
from app.utils.http_client import url_shortener_client
from app.utils.url_shortener import create_amazon_shortlink

from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models.get_items_request import GetItemsRequest
from paapi5_python_sdk.models.get_items_resource import GetItemsResource
from paapi5_python_sdk.models.partner_type import PartnerType
from paapi5_python_sdk.rest import ApiException

class ProductRepositoryError(Exception):
    """Generic product repository error."""

    def __init__(
        self,
        message="An unexpected error occurred while accessing the product repository.",
    ):
        super().__init__(message)


class ProductNotFound(ProductRepositoryError):
    """Raised when a product is not found (HTTP 404)."""

    def __init__(self, url: str):
        super().__init__(f"Product not found at URL: {url}")


class ProductRepository:
    setting: settings.Settings
    amazon_api: DefaultApi

    def __init__(self, setting: settings.Settings):
        self.setting = setting

        amazon_api = DefaultApi(
            access_key=self.setting.AMAZON_ACCESS_KEY,
            secret_key=self.setting.AMAZON_SECRET_KEY,
            host=self.setting.AMAZON_HOST,
            region=self.setting.AMAZON_REGION,
        )

        self.amazon_api = amazon_api

    @staticmethod
    def _resolve_redirect(url: str) -> str:
        try:
            response = url_shortener_client.get(url)
            return str(response.url) 
        except httpx.RequestError as e:
            logger.warning("Failed to resolve redirect for %s: %s", url, str(e))
            raise ProductRepositoryError(f"Error resolving redirect for URL: {url}. Details: {str(e)}")
    
    @staticmethod
    def _extract_asin(url: str) -> str:
        """Pull the 10-char ASIN out of an Amazon URL."""
        m = re.search(r"/([A-Z0-9]{10})(?:[/?]|$)", url)
        if not m:
            raise ProductRepositoryError(f"Could not extract ASIN from URL: {url}")

        return m.group(1)

    def get_product_by_url(self, url: str) -> Product:
        try:
            logger.info("Fetching product from URL: %s", url)

            if "amzn.to" in url or "amazn.com" in url or "amzlink.to" in url:
                logger.info("Shortened URL detected. Resolving...")
                url = ProductRepository._resolve_redirect(url)  

            asin = ProductRepository._extract_asin(url)
            logger.debug("Extracted ASIN: %s", asin)

            request = GetItemsRequest(
                partner_tag=self.setting.AMAZON_PARTNER_TAG,
                partner_type=PartnerType.ASSOCIATES,
                marketplace=self.setting.AMAZON_MARKETPLACE,
                item_ids=[asin],
                resources=[
                    GetItemsResource.ITEMINFO_TITLE,
                    GetItemsResource.IMAGES_PRIMARY_LARGE,
                    GetItemsResource.OFFERSV2_LISTINGS_PRICE,
                    GetItemsResource.OFFERSV2_LISTINGS_DEALDETAILS,
                ],
            )

            response = self.amazon_api.get_items(request)
            logger.info("Received response for ASIN: %s", asin)

            item = response.items_result.items[0]

            image = item.images.primary.large.url
            title = item.item_info.title.display_value
            detail_url = item.detail_page_url

            logger.debug("Parsed item - Title: %s, Image: %s, URL: %s", title, image, detail_url)

            short_url = create_amazon_shortlink(title, detail_url)

            listing = item.offers_v2.listings[0]
            price_section = listing.get('Price', {})
            current_price = price_section.get('Money', {}).get('DisplayAmount')
            
            logger.debug("Item price: %s for ASIN: %s", current_price, asin)

            saving_basis = price_section.get('SavingBasis', {}).get('Money')
            old_price = saving_basis.get('DisplayAmount') if saving_basis else None
            
            logger.info("Successfully converted item to Product: %s", asin)

            return Product(image=image, title=title, url=short_url, price=current_price, old_price=old_price)

        except ApiException as e:
            msg = f"Amazon API Exception (status={e.status})"
            logger.error(msg)
            raise ProductRepositoryError(msg) from e

        except Exception as e:
            msg = f"Unexpected error ({type(e).__name__}): {e}"
            logger.exception(msg)
            raise ProductRepositoryError(msg) from e