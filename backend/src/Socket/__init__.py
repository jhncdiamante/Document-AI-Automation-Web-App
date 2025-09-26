from flask_socketio import SocketIO
from src.flask_config import app

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
    manage_session=False,
    logger=False,
    engineio_logger=False
)