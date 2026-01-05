from django.contrib import admin
from . import models

class BannerAdmin(admin.ModelAdmin):
	list_display=('alt_text','image_tag')
admin.site.register(models.Banners,BannerAdmin)

class ServiceAdmin(admin.ModelAdmin):
	list_display=('title','image_tag')
admin.site.register(models.Service,ServiceAdmin)

class PageAdmin(admin.ModelAdmin):
	list_display=('title',)
admin.site.register(models.Page,PageAdmin)

class GalleryAdmin(admin.ModelAdmin):
	list_display=('title','image_tag')
admin.site.register(models.Gallery,GalleryAdmin)

class GalleryImageAdmin(admin.ModelAdmin):
	list_display=('alt_text','image_tag')
admin.site.register(models.GalleryImage,GalleryImageAdmin)

class AppSettingAdmin(admin.ModelAdmin):
	list_display=('image_tag',)
admin.site.register(models.AppSetting,AppSettingAdmin)


admin.site.register(models.SubGroup)
admin.site.register(models.GroupSubgroupMapping)
