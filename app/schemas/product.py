from pydantic import BaseModel

class Product(BaseModel):
    image: str
    title: str
    url: str
    price: str
    old_price: str | None
    coupon: tuple[str | None, str] | None

