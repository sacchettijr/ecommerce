from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import viewsets
from rest_framework.permissions import AllowAny


@method_decorator(csrf_protect, name="dispatch")
class PublicAuthViewSet(
    viewsets.ViewSet,
):
    #   Base dos endpoints de autenticação. O DRF só exige CSRF de quem já está autenticado;
    #   aqui ele é exigido sempre (inclusive no login), com o token vindo do cookie "csrftoken"
    #   que o endpoint de sessão define.
    permission_classes = (AllowAny,)
