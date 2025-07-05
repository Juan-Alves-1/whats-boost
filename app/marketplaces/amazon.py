import re

from .marketplace import Marketplace
from .marketplace import MarketplaceException

from app.config import settings
from app.schemas.product import Product
from app.utils.logger import logger
from app.utils.url_shortener import create_amazon_shortlink

from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models.get_items_request import GetItemsRequest
from paapi5_python_sdk.models.get_items_resource import GetItemsResource
from paapi5_python_sdk.models.partner_type import PartnerType
from paapi5_python_sdk.rest import ApiException

async def get_amazon_marketplace():
    return AmazonMarketplace(settings.settings)

class AmazonMarketplace(Marketplace):
    setting: settings.Settings
    amazon_api: DefaultApi

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, setting: settings.Settings):
        if self._initialized:
            return

        self.setting = setting

        amazon_api = DefaultApi(
            access_key=self.setting.AMAZON_ACCESS_KEY,
            secret_key=self.setting.AMAZON_SECRET_KEY,
            host=self.setting.AMAZON_HOST,
            region=self.setting.AMAZON_REGION,
        )

        self.amazon_api = amazon_api

        self._initialized = True

    @staticmethod
    def _extract_asin(url: str) -> str:
        """Pull the 10-char ASIN out of an Amazon URL."""
        m = re.search(r"/([A-Z0-9]{10})(?:[/?]|$)", url)
        if not m:
            raise MarketplaceException(f"Could not extract ASIN from URL: {url}")

        return m.group(1)

    def get_product(self, url: str) -> Product:
        try:
            logger.info(f"Fetching product from URL: {url}")

            asin = AmazonMarketplace._extract_asin(url)
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
            logger.info(f"Received response for ASIN: {asin}")

        except ApiException as e:
            msg = f"Amazon API Exception (status={e.status})"
            logger.error(msg)

            raise MarketplaceException(msg) from e

        try:
            item = response.items_result.items[0] #pyright: ignore

            image = item.images.primary.large.url
            title = item.item_info.title.display_value
            detail_url = item.detail_page_url

            logger.debug(f"Parsed item - Title: {title}, Image: {image}, URL: {detail_url}")

            short_url = create_amazon_shortlink(title, detail_url)

            listing = item.offers_v2.listings[0]
            price_section = listing.get('Price', {})
            current_price = price_section.get('Money', {}).get('DisplayAmount')
            
            logger.debug(f"Item price: {current_price} for ASIN: {asin}")

            saving_basis = price_section.get('SavingBasis', {}).get('Money')
            old_price = saving_basis.get('DisplayAmount') if saving_basis else None
            
            logger.info(f"Successfully converted item to Product: {asin}")

            return Product(image=image, title=title, url=short_url, price=current_price, old_price=old_price)

        except Exception as e:
            msg = f"Unexpected error ({type(e).__name__}): {e}"
            logger.exception(msg)
            raise MarketplaceException(msg) from e
