#from amazon_paapi import AmazonApi
import re
from typing import Optional
import paapi5_python_sdk
from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.partner_type import PartnerType
from paapi5_python_sdk.get_items_request import GetItemsRequest
from paapi5_python_sdk.get_items_resource import GetItemsResource
from paapi5_python_sdk.rest import ApiException

from app.config import settings
from app.schemas.product import Product

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

    def __init__(self, setting: settings.Settings):
    # 1) configure the PA-API client
        cfg = paapi5_python_sdk.Configuration(
            access_key=setting.AMAZON_ACCESS_KEY,
            secret_key=setting.AMAZON_SECRET_KEY,
            host="webservices.amazon.com.br",        # or your regional endpoint
            region=setting.AMAZON_COUNTRY,       # e.g. "us-east-1"
        )
        
        self.setting = setting
        self.client = DefaultApi(paapi5_python_sdk.ApiClient(cfg))
        self.partner_tag = setting.AMAZON_PARTNER_TAG
        self.marketplace = setting.AMAZON_COUNTRY
    
    @staticmethod
    def _extract_asin(url: str) -> str:
        """Pull the 10-char ASIN out of an Amazon URL."""
        m = re.search(r"/([A-Z0-9]{10})(?:[/?]|$)", url)
        if not m:
            raise ProductRepositoryError(f"Could not extract ASIN from URL: {url}")
        return m.group(1)

    def get_product_by_url(self, url: str) -> Product:
        try:
            asin = self._extract_asin(url)

            # 2) build our GetItemsRequest, including the OffersV2 fields
            request = GetItemsRequest(
                partner_tag=self.partner_tag,
                partner_type=PartnerType.ASSOCIATES,
                marketplace=self.marketplace,
                item_ids=[asin],
                resources=[
                    # core info
                    GetItemsResource.IMAGES_PRIMARY_LARGE,
                    GetItemsResource.ITEM_INFO_TITLE,
                    GetItemsResource.DETAIL_PAGE_URL,
                    # legacy Offers (fallback)
                    GetItemsResource.OFFERS_LISTINGS_PRICE,
                    # new OffersV2
                    GetItemsResource.OFFERSV2_LISTINGS_PRICE,
                    GetItemsResource.OFFERSV2_LISTINGS_DEALDETAILS,
                    GetItemsResource.OFFERSV2_LISTINGS_SAVINGS,
                ],
            )

            # 3) hit the API
            response = self.client.get_items(request)
            if not response.items_result or not response.items_result.items:
                raise ProductNotFound(url)

            item = response.items_result.items[0]

            # 4) extract common fields
            image = item.images.primary.large.url
            title = item.item_info.title.display_value
            detail_url = item.detail_page_url

            # 5) find the prime-exclusive price if present
            prime_price: Optional[str] = None
            for listing in (item.offers_v2 or []).listings or []:
                if listing.deal_details and listing.deal_details.access_type == "PRIME_EXCLUSIVE":
                    prime_price = listing.price.money.display_amount
                    break

            # 6) fallback to the first (regular) offer if no Prime-only deal
            if prime_price is None:
                if item.offers and item.offers.listings:
                    prime_price = item.offers.listings[0].price.display_amount
                else:
                    raise ProductRepositoryError("No offer price available for this product")

            return Product(
                image=image,
                title=title,
                url=detail_url,
                price=prime_price,
                saving=None,  # you can add savings extraction similarly if you need it
            )

        except ApiException as e:
            raise ProductRepositoryError(f"PA-API error: {e.status} {e.body}")
        except Exception as e:
            raise ProductRepositoryError(str(e))