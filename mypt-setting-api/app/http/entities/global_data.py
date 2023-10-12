from app.http.views.service_logger_view import ServiceLoggerViewSet
from core.entities.redis_service import RedisService

authUserSessionData = None
requestInfo = None
service_logger = ServiceLoggerViewSet()
redis_service = RedisService()

REDIS_SERVICE_RESPONSE = [
    {
        "REDIS_INIT_FAILURE": "REDIS INITIALIZATION FAILED",
        "INSERT_FAIL": "INSERT FAILURE"
    }
]