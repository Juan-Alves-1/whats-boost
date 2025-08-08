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
        self.client = OpenAI(
            base_url=setting.OPENAI_HOST, 
            api_key=setting.OPENAI_KEY,
            max_retries=1      
        )

    def _create_promotional_prompt(
        self, product: Product, max_len: int,
    ) -> str:
        """Create a detailed prompt for generating promotional messages."""

        prompt = f"""
        Create a promotional WhatsApp message according to the following product details:

        - Product title: {product.title}
        - Current price: {product.price}
        - Previous price: {product.old_price}
        - Link direto da promo: {product.url}
        - Maximum size: {max_len} characters

        You must make it sound natural in Brazilian Portuguese.
        """
        return prompt

    def generate_promotional_message(
        self,
        product: Product,
        max_len: int = 360,
        max_token: int = 115,
    ) -> str:
        """
        Generate a promotional message for WhatsApp from product data.

        Args:
            product: Product object containing title, price, and other details
            max_length: Maximum length of the promotional message

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
            You only generate whatsapp messages in Brazilian Portuguese.
            Your writing is concise, emoji-rich and never spammy. 

            Follow the template below and use **two** consecutive newline characters (`\n\n`) to separate each section of your message:
                1. ONE LINE PRODUCT TITLE SUMMARY 
                    - Summary of the title if longer than 32 characters 
                2. PRICE 
                    - Old price 
                    - Lowest price 
                    {else}
                    - Only lowest price 
                3. LINK 
                    - 🔥 Link direto da promo: full affiliate URL
                4. CONSTANT MESSAGE
                    - Simply add the following to the end of the message "✅ Entre no nosso grupo de promos: chat.whatsapp.com/Fc0wDVXB744LrEO1bZeT79"
            
                Example below according to template aforementioned:
                    Example 1:
                        "Pack de Coca-Cola sem açucar\n\n"
                        "De R$ 23"
                        "Por R$ 13 \n\n"
                        "🔥 Link direto da promo: https://amzlink.to/example \n\n"
                        "✅ Entre no nosso grupo de promos: chat.whatsapp.com/Fc0wDVXB744LrEO1bZeT79"

                    Example 2:
                        "Pack de Coca-Cola sem açucar\n\n"
                        "Por R$ 13 \n\n"
                        "🔥 Link direto da promo: https://amzlink.to/example \n\n"
                        "✅ Entre no nosso grupo de promos: chat.whatsapp.com/Fc0wDVXB744LrEO1bZeT79"
            
            Constraints:  
                - Only return the WhatsApp message text. No commentary or markdown
                - Always use full affiliate URL (no URL shorteners)
                - Only include relevant emojis for the product context
            """
                        
            messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]

            response = self.client.chat.completions.create(
                model=self.setting.OPENAI_MODEL,
                messages=messages,
                max_completion_tokens=max_token,
                temperature=0.2,
                top_p=0.95,
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