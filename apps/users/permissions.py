"""
Custom permission classes for role-based access control
"""
from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission for superadmin only
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'SUPERADMIN'
        )


class IsSuperAdminOrAdmin(permissions.BasePermission):
    """
    Permission for superadmin or admin
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['SUPERADMIN', 'ADMIN']
        )


class IsServiceProvider(permissions.BasePermission):
    """
    Permission for service providers
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'SERVICE_PROVIDER'
        )


class IsCustomer(permissions.BasePermission):
    """
    Permission for customers
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'CUSTOMER'
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission for owner of the object or admin
    """
    def has_object_permission(self, request, view, obj):
        # Admins can access anything
        if request.user.role in ['SUPERADMIN', 'ADMIN']:
            return True
        
        # Check if object has user/customer/provider field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'customer'):
            return obj.customer == request.user
        elif hasattr(obj, 'provider'):
            return obj.provider == request.user
        
        return obj == request.user


class IsProviderOrCustomer(permissions.BasePermission):
    """
    Permission for both providers and customers
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['SERVICE_PROVIDER', 'CUSTOMER']
        )