import threading
from django.utils.deprecation import MiddlewareMixin

# Almacenamiento local de thread para el usuario actual
_thread_locals = threading.local()

def get_current_user():
    """Obtiene el usuario actual del contexto del thread"""
    return getattr(_thread_locals, 'user', None)

class CurrentUserMiddleware(MiddlewareMixin):
    """Middleware para almacenar el usuario actual en el contexto del thread"""

    def process_request(self, request):
        """Almacena el usuario actual en el thread local"""
        _thread_locals.user = getattr(request, 'user', None)

    def process_response(self, request, response):
        """Limpia el usuario al finalizar la request"""
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user
        return response

    def process_exception(self, request, exception):
        """Limpia el usuario en caso de excepción"""
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user
        return None