from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('agregar_rubro/', views.agregar_rubro, name='agregar_rubro'),
    path('agregar_bien/', views.agregar_bien, name='agregar_bien'),
    path('agregar_orden/', views.agregar_orden, name='agregar_orden'),
    # Password change URLs
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),

    path('ordenes/', views.ordenes_list, name='ordenes'),
    path('ordenes/<int:pk>/', views.orden_detalle, name='orden_detalle'),
    path('ordenes/<int:pk>/editar/', views.orden_editar, name='orden_editar'),
    path('login/', auth_views.LoginView.as_view(template_name='inventario/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/?logout=1'), name='logout'),
    path('entrega/nueva/', views.crear_entrega, name='crear_entrega'),
    path('remito/<int:pk>/pdf/', views.remito_pdf, name='remito_pdf'),
    path('remito/<int:pk>/imprimir/', views.remito_print, name='remito_print'),
    path('api/orden_bienes/<int:orden_id>/', views.api_orden_bienes, name='api_orden_bienes'),
    path('api/orden_precio/<int:orden_id>/<int:bien_id>/', views.api_orden_precio, name='api_orden_precio'),
    path('api/ordenes_con_stock_bien/<int:bien_id>/', views.api_ordenes_con_stock_bien, name='api_ordenes_con_stock_bien'),
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/stock_rubro/', views.reporte_stock_rubro, name='reporte_stock_rubro'),
    path('reportes/stock_bien/', views.reporte_stock_bien, name='reporte_stock_bien'),
    path('reportes/entregas_anio/', views.reporte_entregas_anio, name='reporte_entregas_anio'),
    path('reportes/entregas_area/', views.reporte_entregas_area, name='reporte_entregas_area'),
    path('reportes/ranking_bienes/', views.reporte_ranking_bienes, name='reporte_ranking_bienes'),
    path('reportes/ranking_proveedores/', views.reporte_ranking_proveedores, name='reporte_ranking_proveedores'),
]
