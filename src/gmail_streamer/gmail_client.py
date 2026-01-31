import base64


def search_messages(service, query: str) -> list[str]:
    """Return all message IDs matching the query."""
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
