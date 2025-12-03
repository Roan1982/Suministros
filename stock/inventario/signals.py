from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog, Rubro, Bien, OrdenDeCompra, OrdenDeCompraItem, Entrega, EntregaItem
from django.contrib.auth import get_user_model
from .middleware.current_user import get_current_user
import json

User = get_user_model()

# Modelos a auditar
AUDITED_MODELS = [
    Rubro,
    Bien,
    OrdenDeCompra,
    OrdenDeCompraItem,
    Entrega,
    EntregaItem,
]

def get_changes(old_instance, new_instance):
    """Compara dos instancias y devuelve los cambios"""
    if not old_instance:
        return None

    changes = {}
    for field in new_instance._meta.fields:
        field_name = field.name
        old_value = getattr(old_instance, field_name, None)
        new_value = getattr(new_instance, field_name, None)

        # Convertir valores para comparación JSON
        if hasattr(old_value, '__str__'):
            old_value = str(old_value)
        if hasattr(new_value, '__str__'):
            new_value = str(new_value)

        if old_value != new_value:
            changes[field_name] = {
                'old': old_value,
                'new': new_value
            }

    return changes if changes else None

@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    """Guarda el estado anterior de la instancia antes de guardar"""
    if sender in AUDITED_MODELS:
        if instance.pk:
            try:
                old_instance = sender.objects.get(pk=instance.pk)
                instance._audit_old_instance = old_instance
            except sender.DoesNotExist:
                instance._audit_old_instance = None
        else:
            instance._audit_old_instance = None

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    """Registra creación y actualización"""
    if sender in AUDITED_MODELS:
        action = 'CREATE' if created else 'UPDATE'
        old_instance = getattr(instance, '_audit_old_instance', None)

        # Obtener usuario actual usando el middleware
        user = get_current_user()
        if user and not user.is_authenticated:
            user = None

        changes = None
        if not created and old_instance:
            changes = get_changes(old_instance, instance)

        # Solo registrar si hay cambios reales o es una creación
        if created or changes:
            content_type = ContentType.objects.get_for_model(instance)
            AuditLog.objects.create(
                user=user,
                action=action,
                content_type=content_type,
                object_id=instance.pk,
                object_repr=str(instance),
                changes=changes
            )

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    """Registra eliminación"""
    if sender in AUDITED_MODELS:
        # Obtener usuario actual usando el middleware
        user = get_current_user()
        if user and not user.is_authenticated:
            user = None

        content_type = ContentType.objects.get_for_model(instance)
        AuditLog.objects.create(
            user=user,
            action='DELETE',
            content_type=content_type,
            object_id=instance.pk,
            object_repr=str(instance),
            changes=None
        )