from rest_framework import serializers
from .models import Rubro, Bien, OrdenDeCompra, Entrega, Servicio

class RubroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rubro
        fields = '__all__'

class BienSerializer(serializers.ModelSerializer):
    rubro_nombre = serializers.CharField(source='rubro.nombre', read_only=True)
    
    class Meta:
        model = Bien
        fields = '__all__'

class OrdenDeCompraSerializer(serializers.ModelSerializer):
    rubro_nombre = serializers.CharField(source='rubro.nombre', read_only=True)
    
    class Meta:
        model = OrdenDeCompra
        fields = '__all__'

class EntregaSerializer(serializers.ModelSerializer):
    orden_compra_numero = serializers.CharField(source='orden_de_compra.numero', read_only=True)
    
    class Meta:
        model = Entrega
        fields = '__all__'

class ServicioSerializer(serializers.ModelSerializer):
    rubro_nombre = serializers.CharField(source='rubro.nombre', read_only=True)
    
    class Meta:
        model = Servicio
        fields = '__all__'