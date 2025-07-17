from pydantic import BaseModel
from typing import Optional

class WebhookMessageUpsertKey(BaseModel):
    remoteJid: str
    fromMe: bool
    id: str
    senderLid: Optional[str] = None

class WebhookMessageSenderKeyDistributionMessage(BaseModel):
    groupId: str
    axolotlSenderKeyDistributionMessage: str

class WebhookMessageImageMessage(BaseModel):
    url: str
    mimetype: str
    caption: Optional[str] = None
    fileSha256: str
    fileLength: str
    mediaKey: str
    fileEncSha256: str
    directPath: str
    contextInfo: Optional[dict] = None

class WebhookMessageUpsertContent(BaseModel):
    conversation: Optional[str] = None
    stickerMessage: Optional[dict] = None
    imageMessage: Optional[WebhookMessageImageMessage] = None
    senderKeyDistributionMessage: Optional[WebhookMessageSenderKeyDistributionMessage] = None
    messageContextInfo: Optional[dict] = None

class WebhookMessageUpsertData(BaseModel):
    key: WebhookMessageUpsertKey
    pushName: str
    status: str
    message: WebhookMessageUpsertContent
    messageType: str
    messageTimestamp: int
    instanceId: str
    source: str

class WebhookEventMessageUpsert(BaseModel):
    event: str
    instance: str
    data: WebhookMessageUpsertData
    destination: str
    date_time: str
    sender: str
    server_url: str
    apikey: str
