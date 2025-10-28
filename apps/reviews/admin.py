"""
Django Admin configuration for Review models
"""
from django.contrib import admin
from apps.reviews.models import Review, ReviewResponse, ReviewImage, ReviewHelpful


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'provider', 'service', 'rating', 'is_verified', 'is_active', 'is_flagged', 'created_at']
    list_filter = ['rating', 'is_verified', 'is_active', 'is_flagged', 'is_featured', 'created_at']
    search_fields = ['customer__email', 'provider__email', 'service__title', 'title', 'comment']
    readonly_fields = ['helpful_count', 'is_verified', 'created_at', 'updated_at']
    inlines = [ReviewImageInline]
    
    fieldsets = (
        ('Review Information', {
            'fields': ('booking', 'customer', 'provider', 'service')
        }),
        ('Rating', {
            'fields': ('rating', 'quality_rating', 'punctuality_rating', 'professionalism_rating', 'value_rating')
        }),
        ('Content', {
            'fields': ('title', 'comment')
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified', 'is_featured', 'is_flagged', 'flagged_reason')
        }),
        ('Moderation', {
            'fields': ('moderated_by', 'moderated_at'),
            'classes': ('collapse',)
        }),
        ('Engagement', {
            'fields': ('helpful_count',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_featured', 'mark_as_flagged', 'mark_as_active']
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
    mark_as_featured.short_description = "Mark selected reviews as featured"
    
    def mark_as_flagged(self, request, queryset):
        queryset.update(is_flagged=True)
    mark_as_flagged.short_description = "Flag selected reviews"
    
    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True, is_flagged=False)
    mark_as_active.short_description = "Mark selected reviews as active"


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ['review', 'provider', 'created_at']
    search_fields = ['review__title', 'provider__email', 'response_text']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__title', 'user__email']