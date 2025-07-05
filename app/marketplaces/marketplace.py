from abc import ABC, abstractmethod

from app.schemas.product import Product

class MarketplaceException(Exception):
    def __init__(
        self,
        message="An unexpected error occurred while accessing the product repository.",
    ):
        super().__init__(message)

class Marketplace(ABC):
    @abstractmethod
    def get_product(self, url: str) -> Product:
        """Fetch a product's information from a given URL"""
        pass

    def __str__(self):
        return f"{self.__class__.__name__} Marketplace"
