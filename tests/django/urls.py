"""URL configuration for Django Inertia tests."""

from django.urls import path

from . import views

urlpatterns = [
    path("test/", views.test_route, name="test"),
    path("multi-props/", views.multi_props_route, name="multi_props"),
    path("nested-props/", views.nested_props_route, name="nested_props"),
    path("deferred-props/", views.deferred_props_route, name="deferred_props"),
    path("once-props/", views.once_props_route, name="once_props"),
    path("reset/", views.reset_route, name="reset"),
    path("history/", views.history_route, name="history"),
    path("with-errors/", views.test_errors, name="with_errors"),
    path("submit/", views.test_submit, name="submit"),
    path("external-redirect/", views.test_external_redirect, name="external_redirect"),
    path("decorator/", views.test_decorator, name="decorator"),
    path("class-view/", views.TestClassView.as_view(), name="class_view"),
]
