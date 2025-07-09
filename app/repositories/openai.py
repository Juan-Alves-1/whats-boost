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
            "enthusiastic": "Sound like a friend sharing an exciting deal—fun. Often be urgent and relatable.",
            "professional": "Use professional tone, focus on product benefits and value proposition.",
            "casual": "Use friendly, conversational tone. Be approachable and relatable.",
        }

        style_instruction = style_instructions.get(
            style, style_instructions["enthusiastic"]
        )

        prompt = f"""
        Create a promotional WhatsApp copy according to the following product details:

        - Product title: {product.title}
        - Current price: {product.price}
        - Previous price: {product.old_price}
        - Link direto da promo: {product.url}
        - Style: {style_instruction}
        - Maximum size: {max_len} characters

        You must make it sound natural in Brazilian Portuguese.
        """
        return prompt

    def generate_promotional_message(
        self,
        product: Product,
        max_len: int = 270,
        max_token: int = 95,
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
            user_prompt = self._create_promotional_prompt(product, max_len, style)
            system_prompt = """
            You are a senior Brazilian copywriter and WhatsApp marketing expert who only writes e-commerce copy in Brazilian Portuguese.
            Your Tone of Voice is punchy, concise, emoji-rich, sometimes a bit sassy or playful, but never spammy. 

            Follow the template below and use **two** consecutive newline characters (`\n\n`) to separate each section of your message:
                1. ONE LINE PRODUCT TITLE SUMMARY (required) 
                    - Make a summary of the title if longer than 32 characters 
                2. BENEFIT (optional) 
                    - Up to one line describing a key selling point 
                3. PRICES (required) 
                    - Old price (struck through) and new price (bold) 
                4. LINK (required)
                    - Link direto da promo: full affiliate URL
            
                Examples below according to template aforementioned:
                    Example 1:
                        "Pack de Coca-Cola sem açucar\n\n"
                        "Hmmm... coca geladinha 😋 \n\n" 
                        "~De R$ 23~ por apenas *R$ 13* \n\n"
                        "Link direto da promo: https://amzlink.to/example"

                    Example 2:
                        "Nivea Hidratante Milk 200ml \n\n"
                        "Deixa sua pele macia como um toque de seda! \n\n"
                        "~De R$ 17~ por apenas *R$ 12* 😱 \n\n"
                        "Link direto da promo: https://amzlink.to/example"

            Constraints:  
                - Only return the WhatsApp message text. No commentary or markdown
                - Always use full affiliate URL (no URL shorteners)
                - Only include relevant emojis for the product context
                - Use 1 exclamation mark maximum for the whole copy
                - Avoid English terms and gendered language
            """
                        
            messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]

            response = self.client.chat.completions.create(
                model=self.setting.OPENAI_MODEL,
                messages=messages,
                max_completion_tokens=max_token,
                temperature=0.6,
                top_p=0.9,
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