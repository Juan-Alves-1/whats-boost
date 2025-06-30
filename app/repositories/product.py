from amazon_paapi import AmazonApi
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
    amazon: AmazonApi

    def __init__(self, setting: settings.Settings):
        self.setting = setting

        self.amazon = AmazonApi(
            self.setting.AMAZON_ACCESS_KEY,
            self.setting.AMAZON_SECRET_KEY,
            self.setting.AMAZON_PARTNER_TAG,
            self.setting.AMAZON_COUNTRY,  # pyright:ignore
        )

    def get_product_by_url(self, url: str) -> Product:
        try:
            item = self.amazon.get_items(url)[0]

            image = item.images.primary.large.url
            title = item.item_info.title.display_value
            url = item.detail_page_url

            if item.offers.listings == None:
                raise ProductRepositoryError(f"This product doesn't have a listing")

            price = item.offers.listings[0].price.display_amount

            saving = None
            if (item.offers.listings[0].price.savings) != None: 
                saving = item.offers.listings[0].price.savings.display_amount

            return Product(image=image, title=title, url=url, price=price, saving=saving)
        except Exception as e:
            raise ProductRepositoryError(f"An unexpected error occurred: {str(e)}")


