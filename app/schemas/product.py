from pydantic import BaseModel
from jinja2 import Template

class Product(BaseModel):
    image: str
    title: str
    url: str
    price: str
    old_price: str | None

    def __str__(self):
        # TODO: Move this to a separate template file.
        # TODO: Add emojis.
        template_str = """{{ product.title }}
{% if product.old_price %}
De: {{ product.old_price }}
Por: {{ product.price }}
{% else %}
Por: {{ product.price }}
{% endif %}
Link direto da promo: {{ product.url }}"""

        try:
            template = Template(template_str)

            message = template.render(product=self)

            return message.strip()
        except Exception as e:
            raise Exception(f"Error generating promotional message: {e}") from e
