from pydantic import BaseModel, Field, HttpUrl, StringConstraints, model_validator
from typing import Annotated, List

# Annotated aliases for reusability
GroupID = Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, pattern=r"@g\.us$")]
Caption = Annotated[str, StringConstraints(strip_whitespace=True, min_length=15, max_length=400)]
MediaType = Annotated[str, StringConstraints(to_lower=True)]
MimeType = Annotated[str, StringConstraints(to_lower=True)]
Delay = Annotated[int, Field(ge=10, le=60)]

class bulk_media_payload(BaseModel):
    group_ids: List[GroupID]
    caption: Caption
    media_url: HttpUrl
    min_delay_sec: Delay = 18
    max_delay_sec: Delay = 25
    mediatype: MediaType = "image"
    mimetype: MimeType = "image/jpg"
    
    def model_post_init(self, __context) -> None:
        self.media_url = str(self.media_url)  # Convert to plain string

@model_validator(mode="after")
def validate_delay_range(self) -> "bulk_media_payload":
    if self.max_delay_sec < self.min_delay_sec:
        raise ValueError("max_delay_sec must be greater than or equal to min_delay_sec")
    return self
