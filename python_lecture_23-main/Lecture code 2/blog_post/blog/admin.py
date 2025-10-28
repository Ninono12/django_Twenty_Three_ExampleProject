from django.contrib import admin
from blog.models import BlogPost, BlogPostImage, Author, BlogPostCover


admin.site.register(BlogPostImage)
admin.site.register(Author)
admin.site.register(BlogPostCover)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'deleted', 'category', 'published', 'archived')
    list_editable = ('is_active', 'deleted')
    list_filter = ('is_active', 'category', 'deleted', 'created_at')
    search_fields = ('title', 'text')
    filter_horizontal = ('authors',)  # for ManyToMany fields

    # Optional: make fields read-only
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('title', 'text', 'owner', 'is_active', 'category', 'order')
        }),
        ('Files & Links', {
            'fields': ('website', 'document')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
        ('Status', {
            'fields': ('deleted', 'published', 'archived')
        }),
    )
