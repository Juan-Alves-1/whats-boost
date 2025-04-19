import bleach
from pydantic import BaseModel, Field, HttpUrl, StringConstraints, field_validator, model_validator
from typing import Annotated, List

# Annotated aliases for reusability
GroupID = Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, pattern=r"@g\.us$")]
Caption = Annotated[str, StringConstraints(strip_whitespace=False, min_length=15, max_length=400)]
MediaType = Annotated[str, StringConstraints(to_lower=True)]
MimeType = Annotated[str, StringConstraints(to_lower=True)]
Delay = Annotated[int, Field(ge=10, le=60)]

# Deterministic and free of I/O and side effects 
class bulk_media_payload(BaseModel):
    group_ids: List[GroupID]
    caption: Caption
    media_url: HttpUrl
    min_delay_sec: Delay = 18
    max_delay_sec: Delay = 25
    mediatype: MediaType = "image"
    mimetype: MimeType = "image/jpg"

    @field_validator("caption") # Pydantic v2 method decorator that runs validation logic on a given field before or after standard validation occurs
    @classmethod    # Built-in decorator that allows a method to receive the cls (class itself) instead of an instance (self)
    def sanitise_caption(cls, value: str) -> str:
        cleaned = bleach.clean(
            value,
            tags=[],           # no tags allowed
            attributes={},     # no attributes allowed
            strip=True         # remove disallowed tags instead of escaping
        )
        return cleaned

    @model_validator(mode="after")  # Pydantic v2 model-wide validator that runs after all fields have been validated (cross-field dependencies)
    def validate_delay_range(self) -> "bulk_media_payload":
        if self.max_delay_sec < self.min_delay_sec:
            raise ValueError("max_delay_sec must be greater than or equal to min_delay_sec")
        return self

    # Mutate field after validation
    def model_post_init(self, __context) -> None:
        self.media_url = str(self.media_url)  # Convert to plain string