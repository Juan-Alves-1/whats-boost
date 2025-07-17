import re
import httpx

from fastapi import APIRouter

from app.schemas.webhooks import WebhookEventMessageUpsert
from app.utils.logger import logger
from app.controllers.api.link_api_controller import product_repository
from app.config import settings

router = APIRouter()

# TODO: Add group IDs to watch for messages.
# TODO: Group IDs should be loaded into the system from a configuration file or database.
GROUP_IDS_TO_WATCH = []

@router.post("/api/v1/webhooks/messages", name="webhook_messages")
async def webhooks_message(
    message: WebhookEventMessageUpsert,
):
    logger.debug("Received webhook message:", message)

    if message.data.key.remoteJid not in GROUP_IDS_TO_WATCH:
        logger.error(f"Message from {message.data.key.remoteJid} is not in watched groups. Ignoring.")

        return {"status": "ignored", "reason": "Not a watched group"}

    if message.data.key.fromMe:
        logger.error("Message is from me. Ignoring.")

        return {"status": "ignored", "reason": "Message is from me"}

    if not message.data.message.imageMessage:
        logger.error("No image message found in the webhook data.")

        return {"status": "ignored", "reason": "No image message found"}

    if not message.data.message.imageMessage.caption:
        logger.error("No caption found in image message.")

        return {"status": "ignored", "reason": "No caption found in image message"}

    if "https://" not in message.data.message.imageMessage.caption:
        logger.error("No link found in caption.")

        return {"status": "ignored", "reason": "No link found in caption"}


    logger.debug("Caption found in image message:", message.data.message.imageMessage.caption)

    try:
        links = re.findall(r'https?://[^\s]+', message.data.message.imageMessage.caption)
        if not links:
            logger.error("No valid link found in caption.")

            return {"status": "ignored", "reason": "No valid link found in caption"}

        logger.debug(f"Links found in caption: {links}")

        for link in links:
            try:
                response = httpx.get(link, follow_redirects=True)
                if response.status_code != 200:
                    logger.error(f"Failed to resolve link: {link} with status code {response.status_code}")

                    continue

                full_link = response.url
                logger.debug(f"Resolved link: {full_link}")

                if settings.settings.AMAZON_MARKETPLACE not in str(full_link):
                    logger.error(f"Link is not from Amazon: {full_link}")

                    continue

                product = product_repository.get_product_by_url(str(full_link))

                logger.info(f"Product found: {product}")

                # TODO: Check if the product was already processed recently.
                # We could use a cache or a database to store processed products.

                break
            except Exception as e:
                logger.error(f"Error processing link {link}: {str(e)}")

                continue
    except Exception as e:
        logger.error(f"Error processing webhook message: {str(e)}")

        return {"status": "error", "message": str(e)}

    return {"status": "success", "message": "Webhook processed successfully"}
