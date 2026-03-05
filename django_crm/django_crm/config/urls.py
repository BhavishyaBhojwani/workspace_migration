from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    # API routes
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.v1.urls")),
    
    # Auth routes
    path("", TemplateView.as_view(template_name="auth/login.html"), name="home"),
    path("login/", TemplateView.as_view(template_name="auth/login.html"), name="login"),
    path("register/", TemplateView.as_view(template_name="auth/register.html"), name="register"),
    
    # Dashboard
    path("dashboard/", TemplateView.as_view(template_name="dashboard.html"), name="dashboard"),
    
    # Organisations CRUD
    path("organisations/", TemplateView.as_view(template_name="organisations/index.html"), name="organisations-list"),
    path("organisations/create/", TemplateView.as_view(template_name="organisations/create.html"), name="organisations-create"),
    re_path(r"^organisations/(?P<id>\d+)/$", TemplateView.as_view(template_name="organisations/show.html"), name="organisations-show"),
    re_path(r"^organisations/(?P<id>\d+)/edit/$", TemplateView.as_view(template_name="organisations/edit.html"), name="organisations-edit"),
    
    # People CRUD
    path("people/", TemplateView.as_view(template_name="people/index.html"), name="people-list"),
    path("people/create/", TemplateView.as_view(template_name="people/create.html"), name="people-create"),
    re_path(r"^people/(?P<id>\d+)/$", TemplateView.as_view(template_name="people/show.html"), name="people-show"),
    re_path(r"^people/(?P<id>\d+)/edit/$", TemplateView.as_view(template_name="people/edit.html"), name="people-edit"),
    
    # Leads CRUD
    path("leads/", TemplateView.as_view(template_name="leads/index.html"), name="leads-list"),
    path("leads/create/", TemplateView.as_view(template_name="leads/create.html"), name="leads-create"),
    re_path(r"^leads/(?P<id>\d+)/$", TemplateView.as_view(template_name="leads/show.html"), name="leads-show"),
    re_path(r"^leads/(?P<id>\d+)/edit/$", TemplateView.as_view(template_name="leads/edit.html"), name="leads-edit"),
    
    # Deals CRUD
    path("deals/", TemplateView.as_view(template_name="deals/index.html"), name="deals-list"),
    path("deals/create/", TemplateView.as_view(template_name="deals/create.html"), name="deals-create"),
    re_path(r"^deals/(?P<id>\d+)/$", TemplateView.as_view(template_name="deals/show.html"), name="deals-show"),
    re_path(r"^deals/(?P<id>\d+)/edit/$", TemplateView.as_view(template_name="deals/edit.html"), name="deals-edit"),
    
    # Quotes CRUD
    path("quotes/", TemplateView.as_view(template_name="quotes/index.html"), name="quotes-list"),
    path("quotes/create/", TemplateView.as_view(template_name="quotes/create.html"), name="quotes-create"),
    re_path(r"^quotes/(?P<id>\d+)/$", TemplateView.as_view(template_name="quotes/show.html"), name="quotes-show"),
    re_path(r"^quotes/(?P<id>\d+)/edit/$", TemplateView.as_view(template_name="quotes/edit.html"), name="quotes-edit"),
    
    # Activities CRUD
    path("activities/", TemplateView.as_view(template_name="activities/index.html"), name="activities-list"),
    path("activities/create/", TemplateView.as_view(template_name="activities/create.html"), name="activities-create"),
    re_path(r"^activities/(?P<id>\d+)/$", TemplateView.as_view(template_name="activities/show.html"), name="activities-show"),
    re_path(r"^activities/(?P<id>\d+)/edit/$", TemplateView.as_view(template_name="activities/edit.html"), name="activities-edit"),
    
    # Orders CRUD
    path("orders/", TemplateView.as_view(template_name="orders/index.html"), name="orders-list"),
    path("orders/create/", TemplateView.as_view(template_name="orders/create.html"), name="orders-create"),
    re_path(r"^orders/(?P<id>\d+)/$", TemplateView.as_view(template_name="orders/show.html"), name="orders-show"),
    re_path(r"^orders/(?P<id>\d+)/edit/$", TemplateView.as_view(template_name="orders/edit.html"), name="orders-edit"),
    
    # Invoices CRUD
    path("invoices/", TemplateView.as_view(template_name="invoices/index.html"), name="invoices-list"),
    path("invoices/create/", TemplateView.as_view(template_name="invoices/create.html"), name="invoices-create"),
    re_path(r"^invoices/(?P<id>\d+)/$", TemplateView.as_view(template_name="invoices/show.html"), name="invoices-show"),
    re_path(r"^invoices/(?P<id>\d+)/edit/$", TemplateView.as_view(template_name="invoices/edit.html"), name="invoices-edit"),
    
    # Deliveries CRUD
    path("deliveries/", TemplateView.as_view(template_name="deliveries/index.html"), name="deliveries-list"),
    path("deliveries/create/", TemplateView.as_view(template_name="deliveries/create.html"), name="deliveries-create"),
    re_path(r"^deliveries/(?P<id>\d+)/$", TemplateView.as_view(template_name="deliveries/show.html"), name="deliveries-show"),
    re_path(r"^deliveries/(?P<id>\d+)/edit/$", TemplateView.as_view(template_name="deliveries/edit.html"), name="deliveries-edit"),
    
    # Purchase Orders CRUD
    path("purchase-orders/", TemplateView.as_view(template_name="purchase-orders/index.html"), name="purchase-orders-list"),
    path("purchase-orders/create/", TemplateView.as_view(template_name="purchase-orders/create.html"), name="purchase-orders-create"),
    re_path(r"^purchase-orders/(?P<id>\d+)/$", TemplateView.as_view(template_name="purchase-orders/show.html"), name="purchase-orders-show"),
    re_path(r"^purchase-orders/(?P<id>\d+)/edit/$", TemplateView.as_view(template_name="purchase-orders/edit.html"), name="purchase-orders-edit"),
    
    # Clients
    path("clients/", TemplateView.as_view(template_name="clients/index.html"), name="clients-list"),
    
    # Users CRUD
    path("users/", TemplateView.as_view(template_name="users/index.html"), name="users-list"),
    path("users/create/", TemplateView.as_view(template_name="users/create.html"), name="users-create"),
    re_path(r"^users/(?P<id>\d+)/$", TemplateView.as_view(template_name="users/show.html"), name="users-show"),
    re_path(r"^users/(?P<id>\d+)/edit/$", TemplateView.as_view(template_name="users/edit.html"), name="users-edit"),
    
    # Teams CRUD
    path("teams/", TemplateView.as_view(template_name="teams/index.html"), name="teams-list"),
    path("teams/create/", TemplateView.as_view(template_name="teams/create.html"), name="teams-create"),
    re_path(r"^teams/(?P<id>\d+)/$", TemplateView.as_view(template_name="teams/show.html"), name="teams-show"),
    re_path(r"^teams/(?P<id>\d+)/edit/$", TemplateView.as_view(template_name="teams/edit.html"), name="teams-edit"),
    
    # Products CRUD
    path("products/", TemplateView.as_view(template_name="products/index.html"), name="products-list"),
    path("products/create/", TemplateView.as_view(template_name="products/create.html"), name="products-create"),
    re_path(r"^products/(?P<id>\d+)/$", TemplateView.as_view(template_name="products/show.html"), name="products-show"),
    re_path(r"^products/(?P<id>\d+)/edit/$", TemplateView.as_view(template_name="products/edit.html"), name="products-edit"),
    
    # Settings
    path("settings/", TemplateView.as_view(template_name="settings/index.html"), name="settings"),
]