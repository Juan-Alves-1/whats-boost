from openai import OpenAI
from app.schemas.product import Product
from app.config import settings

class OpenAIRepositoryError(Exception):
    """Generic OpenAI repository error."""

    def __init__(
        self, message="An unexpected error occurred while accessing the OpenAI API."
    ):
        super().__init__(message)


class OpenAIAPIError(OpenAIRepositoryError):
    """Raised when OpenAI API returns an error."""

    def __init__(self, error_message: str):
        super().__init__(f"OpenAI API error: {error_message}")


class OpenAIRateLimitError(OpenAIRepositoryError):
    """Raised when OpenAI API rate limit is exceeded."""

    def __init__(self):
        super().__init__("OpenAI API rate limit exceeded. Please try again later.")


class OpenAIRepository:
    setting: settings.Settings
    client: OpenAI

    def __init__(self, setting: settings.Settings):
        self.setting = setting
        self.client = OpenAI(base_url=setting.OPENAI_HOST, api_key=setting.OPENAI_KEY)

    def _create_promotional_prompt(
        self, product: Product, max_len: int
    ) -> str:
        """Create a detailed prompt for generating promotional messages."""

        prompt = f"""
        - Product title: {product.title}
        - Price: {product.price}
        - Previous price: {product.old_price}
        - Product URL: {product.url}
        """
        return prompt

    def generate_promotional_message(
        self,
        product: Product,
        max_len: int = 270,
        max_token: int = 95,
    ) -> str:
        """
        Generate a promotional message for WhatsApp from product data.

        Args:
            product: Product object containing title, price, and other details
            max_length: Maximum length of the promotional message
            style: Style of the message ('enthusiastic', 'professional', 'casual')

        Returns:
            Generated promotional message as string

        Raises:
            OpenAIAPIError: When API returns an error
            OpenAIRateLimitError: When rate limit is exceeded
            OpenAIRepositoryError: For other unexpected errors
        """
        try:
            user_prompt = self._create_promotional_prompt(product, max_len)
            system_prompt = """
            CONSTRAINTS:  
                - Only return the WhatsApp message text. No commentary or markdown
                - Always use full affiliate URL (no URL shorteners)
                - Only include relevant emojis for the product context

            TEMPLATE:
                PRODUCT_TITLE

                {if PREVIOUS_PRICE is present}
                De: PREVIOUS_PRICE
                Por: CURRENT_PRICE

                {else}
                Por: CURRENT_PRICE

                :fire Link da promo:
                PRODUCT_URL

                ✅Vagas para entrar no grupo de alerta de brindes e promos. Entre grátis aqui: https://chat.whatsapp.com/EfXu2fIKI7I6Y192OukL4Z
            """
                        
            messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]

            response = self.client.chat.completions.create(
                model=self.setting.OPENAI_MODEL,
                messages=messages,
                temperature=0.2,
                frequency_penalty=0.2,
                presence_penalty=0.1,
            )

            if not response.choices or not response.choices[0].message:
                raise OpenAIAPIError("Empty response from OpenAI API")

            content = response.choices[0].message.content
            if content is None:
                raise OpenAIRepositoryError()

            return content

        except Exception as e:
            if hasattr(e, "status_code"):
                raise OpenAIAPIError(str(e))

            if "rate limit" in str(e).lower():
                raise OpenAIRateLimitError()

            raise OpenAIRepositoryError(f"An unexpected error occurred: {str(e)}")
