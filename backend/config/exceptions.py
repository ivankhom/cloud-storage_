import logging
from rest_framework.views import exception_handler

logger = logging.getLogger("app")


def custom_exception_handler(exc, context):
    """
    Приводит все ошибки DRF к единому формату:
    {"error": "текст сообщения", "details": {...опционально...}}
    и логирует их.
    """
    response = exception_handler(exc, context)

    if response is not None:
        detail = response.data
        message = None
        if isinstance(detail, dict) and "detail" in detail and len(detail) == 1:
            message = str(detail["detail"])
            payload = {"error": message}
        elif isinstance(detail, dict):
            message = "; ".join(f"{k}: {v}" for k, v in detail.items())
            payload = {"error": message, "details": detail}
        else:
            message = str(detail)
            payload = {"error": message}

        request = context.get("request")
        logger.warning(
            "API error %s on %s: %s",
            response.status_code,
            getattr(request, "path", "?"),
            message,
        )
        response.data = payload
    else:
        logger.error("Unhandled exception: %s", exc, exc_info=True)

    return response
