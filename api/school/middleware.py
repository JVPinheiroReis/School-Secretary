import logging
from datetime import datetime

from django.utils.deprecation import MiddlewareMixin


class LogUserExceptionMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Detecta login no endpoint de token sem expor os tokens JWT nos logs
        if request.path.endswith("/api/users/token/") and response.status_code == 200:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(
                f"[{timestamp}] Login bem-sucedido detectado no endpoint '{request.path}'"
            )

        # Detecta criação, edição e deleção de dados
        user = getattr(request, "user", None)
        username = (
            getattr(user, "name", None)
            if user and hasattr(user, "is_authenticated") and user.is_authenticated
            else None
        )
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Só loga se for usuário autenticado e tiver username
        if username:
            # Criação
            if request.method == "POST" and response.status_code in [200, 201]:
                logging.info(
                    f"[{timestamp}] CRIAÇÃO detectada por '{username}' no endpoint '{request.path}'"
                )
            # Edição
            if request.method in ["PUT", "PATCH"] and response.status_code in [
                200,
                202,
            ]:
                logging.info(
                    f"[{timestamp}] EDIÇÃO detectada por '{username}' no endpoint '{request.path}'"
                )
            # Deleção
            if request.method == "DELETE" and response.status_code in [200, 204]:
                logging.info(
                    f"[{timestamp}] DELETE detectado por '{username}' no endpoint '{request.path}'"
                )
        return response

    def process_exception(self, request, exception):
        user = getattr(request, "user", None)
        username = user.name if user and user.is_authenticated else "Anonymous"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.error(f"[{timestamp}] Exception for user '{username}': {exception}")
