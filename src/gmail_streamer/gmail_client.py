import base64
from datetime import datetime, timezone


def search_messages(
    service, query: str, after_date: str | None = None, before_date: str | None = None
) -> list[str]:
    """Return all message IDs matching the query.

    If after_date/before_date (YYYY-MM-DD) are provided, appends Gmail date filters.
    """
    if after_date:
        query = f"{query} after:{after_date}"
    if before_date:
        query = f"{query} before:{before_date}"
    ids = []
    request = service.users().messages().list(userId="me", q=query)
    while request:
        response = request.execute()
        for msg in response.get("messages", []):
            ids.append(msg["id"])
        request = service.users().messages().list_next(request, response)
    return ids


def fetch_raw_message(service, msg_id: str) -> bytes:
    """Fetch the full RFC 2822 message as bytes."""
    msg = service.users().messages().get(userId="me", id=msg_id, format="raw").execute()
    return base64.urlsafe_b64decode(msg["raw"])


def fetch_message_metadata(service, msg_id: str) -> dict:
    """Fetch message metadata and return a dict with key fields."""
    msg = service.users().messages().get(
        userId="me", id=msg_id, format="metadata",
        metadataHeaders=["From", "To", "Subject", "Date"],
    ).execute()

    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
    internal_ts = int(msg.get("internalDate", "0")) / 1000
    internal_date = datetime.fromtimestamp(internal_ts, tz=timezone.utc).strftime("%Y-%m-%d")

    return {
        "id": msg_id,
        "date": internal_date,
        "subject": headers.get("Subject", ""),
        "from": headers.get("From", ""),
        "to": headers.get("To", ""),
        "snippet": msg.get("snippet", ""),
        "label_ids": msg.get("labelIds", []),
    }


def fetch_attachments(service, msg_id: str) -> list[dict]:
    """Return list of {filename, data} for each attachment."""
    msg = service.users().messages().get(userId="me", id=msg_id).execute()
    attachments = []
    for part in msg.get("payload", {}).get("parts", []):
        filename = part.get("filename")
        body = part.get("body", {})
        attachment_id = body.get("attachmentId")
        if filename and attachment_id:
            att = (
                service.users()
                .messages()
                .attachments()
                .get(userId="me", messageId=msg_id, id=attachment_id)
                .execute()
            )
            data = base64.urlsafe_b64decode(att["data"])
            attachments.append({"filename": filename, "data": data})
    return attachments
