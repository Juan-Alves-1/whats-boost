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
        self, product: Product, max_len: int, style: str
    ) -> str:
        """Create a detailed prompt for generating promotional messages."""

        style_instructions = {
            "enthusiastic": "Use exciting language, emojis, and create urgency. Be energetic and persuasive.",
            "professional": "Use professional tone, focus on product benefits and value proposition.",
            "casual": "Use friendly, conversational tone. Be approachable and relatable.",
        }

        style_instruction = style_instructions.get(
            style, style_instructions["enthusiastic"]
        )

        prompt = f"""
Create a promotional WhatsApp message for the following product:

Product Title: {product.title}
Price: {product.price}
Saving: {product.saving}
Product URL: {product.url}

Requirements:
- In portuguese
- Only the message; nothing more
- Maximum {max_len} characters
- Style: {style_instruction}
- Include relevant emojis for WhatsApp
- Include product url completely
- Include a call-to-action
- Make it engaging and likely to drive clicks/purchases
- Format for WhatsApp sharing
- Don't short the links becuase of affiliate tag

Focus on creating urgency and highlighting the product's appeal. Make it something people would want to share or click on immediately.
"""
        return prompt

    def generate_promotional_message(
        self,
        product: Product,
        max_len: int = 300,
        max_token: int = 200,
        style: str = "enthusiastic",
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
            # Create the prompt for generating promotional message
            prompt = self._create_promotional_prompt(product, max_len, style)

            response = self.client.chat.completions.create(
                model=self.setting.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a marketing expert specializing in creating engaging WhatsApp promotional messages. Create compelling messages that drive sales while being concise and WhatsApp-friendly.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_token,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
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
