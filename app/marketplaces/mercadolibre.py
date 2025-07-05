from app.schemas.product import Product

from .marketplace import Marketplace

class MercadoLibreMarketplace(Marketplace):
    def get_product(self, url) -> Product:
        print(f"[MercadoLibre] Obteniendo producto desde: {url}")

        return Product(image="", title="", url="", price="", old_price=None)
