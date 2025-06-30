from fastapi import HTTPException, status, Depends
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel, HttpUrl
from app.config import settings
from app.repositories.openai import OpenAIAPIError, OpenAIRateLimitError, OpenAIRepository, OpenAIRepositoryError
from app.repositories.product import ProductRepository, ProductNotFound, ProductRepositoryError
from app.dependencies.auth import auth_required

# TODO: Move this definition to a more appropriate location.
product_repository: ProductRepository = ProductRepository(settings.settings)

# TODO: Move this definition to a more appropriate location.
openai_repository: OpenAIRepository = OpenAIRepository(settings.settings)

router = APIRouter()

class LinkInput(BaseModel):
    """Schema for the input of the link message generation."""
    url: HttpUrl

class LinkOutput(BaseModel):
    """Schema for the output of the link message generation."""
    image: str
    message: str

@router.post("/api/v1/messages/link", name="link_message")
async def link(
    input: LinkInput,
    user=Depends(auth_required)
) -> LinkOutput:
    try:
        product = product_repository.get_product_by_url(str(input.url))

        message = openai_repository.generate_promotional_message(product)

        return LinkOutput(image=product.image, message=message)

    except ProductNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ProductRepositoryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    except OpenAIRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )

    except OpenAIAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="An error occurred while communicating with the OpenAI API. Please try again."
        )

    except OpenAIRepositoryError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while processing your request. Please contact support."
        )
