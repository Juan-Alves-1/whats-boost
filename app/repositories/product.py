import re

from app.config import settings
from app.schemas.product import Product

from app.utils.logger import logger
from app.utils.url_shortener import create_amazon_shortlink

from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.models.get_items_request import GetItemsRequest
from paapi5_python_sdk.models.get_items_resource import GetItemsResource
from paapi5_python_sdk.models.partner_type import PartnerType
from paapi5_python_sdk.rest import ApiException

import httpx

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
    def _extract_asin(url: str) -> str:
        """Pull the 10-char ASIN out of an Amazon URL."""
        m = re.search(r"/([A-Z0-9]{10})(?:[/?]|$)", url)
        if not m:
            raise ProductRepositoryError(f"Could not extract ASIN from URL: {url}")

        return m.group(1)

    def get_product_by_url(self, url: str) -> Product:
        try:
            logger.info("Fetching product from URL: %s", url)

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

            coupon = None

            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                }

                response = httpx.get(
                    f"https:/{self.setting.AMAZON_MARKETPLACE}/dp/{asin}",
                    follow_redirects=True,
                    timeout=15.0,
                    headers=headers)

                response.raise_for_status()
                body = response.text

                code_matches = re.finditer(r'id="promoMessageCXCWpctch[^"]*"[^>]*>\s*(?:Salve\s+o\s+cupom|cupom)\s+(\d+)%:\s*([A-Z0-9]{8})', body, re.IGNORECASE | re.DOTALL)
                for match in code_matches:
                    percentage, code = match.groups()
                    if code and percentage:
                        logger.info("Found coupon code: %s with %s%% discount", code, percentage)

                        coupon = (code, f"{percentage}%")
                        break

                if not coupon:
                    amount_matches = re.finditer(r'Aplicar\s+Cupom\s+de\s+R\$(\d+)', body, re.IGNORECASE)
                    for match in amount_matches:
                        amount = match.group(1)
                        if amount:
                            logger.info("Found direct discount: R$%s", amount)
                            coupon = (None, f"R${amount}")
                            break

                if not coupon:
                    percent_matches = re.finditer(r'Cupom\s+de\s+(?:desconto\s+de\s+)?(\d+)%', body, re.IGNORECASE)
                    for match in percent_matches:
                        percentage = match.group(1)
                        if percentage:
                            logger.info("Found percentage discount: %s%%", percentage)
                            coupon = (None, f"{percentage}%")
                            break

                if not coupon:
                    applied_matches = re.finditer(r'Cupom\s+de\s+desconto\s+de\s+R\$(\d+)\s+aplicado', body, re.IGNORECASE)
                    for match in applied_matches:
                        amount = match.group(1)
                        if amount:
                            logger.info("Found applied discount: R$%s", amount)
                            coupon = (None, f"R${amount}")
                            break

                if not coupon:
                    logger.info("No coupons found for ASIN %s", asin)

            except Exception as e:
                logger.error("Failed to get coupon code for ASIN %s: %s", asin, e)

                coupon = None

            logger.info("Successfully converted item to Product: %s", asin)

            return Product(
                image=image,
                title=title,
                url=short_url,
                price=current_price,
                old_price=old_price,
                coupon=coupon
            )

        except ApiException as e:
            msg = f"Amazon API Exception (status={e.status})"
            logger.error(msg)
            raise ProductRepositoryError(msg) from e

        except Exception as e:
            msg = f"Unexpected error ({type(e).__name__}): {e}"
            logger.exception(msg)
            raise ProductRepositoryError(msg) from e
