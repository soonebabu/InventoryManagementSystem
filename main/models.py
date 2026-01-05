from django.db import models
from django.utils.html import mark_safe
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django import forms
import json
import uuid
from django.utils import timezone
import nepali_datetime
from nepali_datetime_field.models import NepaliDateField
from django.core.exceptions import ValidationError  # Import ValidationError


# Banners
class Banners(models.Model):
	img=models.ImageField(upload_to="banners/")
	alt_text=models.CharField(max_length=150)

	class Meta:
		verbose_name_plural='Banners'

	def __str__(self):
		return self.alt_text

	def image_tag(self):
		return mark_safe('<img src="%s" width="50" />' % (self.img.url))

# Create your models here.
class Service(models.Model):
	title=models.CharField(max_length=150)
	detail=models.TextField()
	img=models.ImageField(upload_to="services/",null=True)

	def __str__(self):
		return self.title

	def image_tag(self):
		return mark_safe('<img src="%s" width="80" />' % (self.img.url))

# Pages
class Page(models.Model):
	title=models.CharField(max_length=200)
	detail=models.TextField()

	def __str__(self):
		return self.title



# Gallery Model
class Gallery(models.Model):
	title=models.CharField(max_length=150)
	detail=models.TextField()
	img=models.ImageField(upload_to="gallery/",null=True)

	def __str__(self):
		return self.title

	def image_tag(self):
		return mark_safe('<img src="%s" width="80" />' % (self.img.url))

# Gallery Images
class GalleryImage(models.Model):
	gallery=models.ForeignKey(Gallery, on_delete=models.CASCADE,null=True)
	alt_text=models.CharField(max_length=150)
	img=models.ImageField(upload_to="gallery_imgs/",null=True)

	def __str__(self):
		return self.alt_text

	def image_tag(self):
		return mark_safe('<img src="%s" width="80" />' % (self.img.url))


class AppSetting(models.Model):
	logo_img=models.ImageField(upload_to='app_logos/')

	def image_tag(self):
		return mark_safe('<img src="%s" width="80" />' % (self.logo_img.url))

# Add Sub Group

from django.contrib.auth.models import Group




def item_photo_upload_path(instance, filename):
    # Constructing the filename using storeDate and primary key
    return f'item_photos/additem/{instance.name}_{instance.storeDate}_{instance.pk}_{filename}'

def changestatus_photo_upload_path(instance, filename):
    return f'item_photos/changestatus/{instance.name}_{instance.pk}_{filename}'

    
def returnitem_photo_upload_path(instance, filename):
    return f'item_photos/returnitem/{instance.name}_{instance.returnDate}_{instance.pk}_{filename}'
    
def requestitem_photo_upload_path(instance, filename):
    return f'item_photos/requestitem/{instance.item_name}_{instance.pk}_{filename}'
    
class RequestItemCount(models.Model):
    UNIT_CHOICES = [
    ('Pcs', 'Pcs'),
    ('Dozen', 'Dozen'),
    ('Mtrs', 'Mtrs'),
    ('Feet', 'Feet'),
    ('Kilogram', 'Kilogram'),
    ('Liters', 'Liters'),
    ('Square Meter', 'Square Meter'),
    ('Cubic Meter', 'Cubic Meter'),
]

    # date = models.DateField()
    name = models.CharField(max_length=100)
    requestDate = models.DateTimeField(auto_now_add=True, null=True)  # Add timestamp for request date

    # item_count = models.IntegerField()
    # requestitem_photo = models.ImageField(upload_to=requestitem_photo_upload_path, blank=True, null=True)
    quantity = models.FloatField(default=1.0)  # Add quantity field
    unit = models.CharField(max_length=50, blank=True, null=True, choices=UNIT_CHOICES)

    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests', null=True)
    description = models.CharField(blank=True, null=True)
    requestitem_photo = models.ImageField(upload_to=requestitem_photo_upload_path, blank=True, null=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')





    def __str__(self):
        return f"{self.requestDate}: {self.name} - {self.quantity} {self.unit}"


class SubGroup(models.Model):
    name = models.CharField(max_length=100)
    parent_group = models.ForeignKey(Group, related_name='subgroups', on_delete=models.CASCADE)
    users = models.ManyToManyField('auth.User', related_name='subgroups', blank=True)
    requested_items = models.ManyToManyField(RequestItemCount, related_name='subgroups', blank=True)


    def __str__(self):
        return self.name

    def clean(self):
        existing_subgroups = SubGroup.objects.filter(name=self.name, parent_group=self.parent_group)
        if self.pk:  # Exclude the current instance when checking for duplicates
            existing_subgroups = existing_subgroups.exclude(pk=self.pk)
        if existing_subgroups.exists():
            raise ValidationError("A subgroup with this name already exists under the selected parent group.")

class GroupSubgroupMapping(models.Model):
    group = models.ForeignKey(Group, related_name='subgroup_mapping', on_delete=models.CASCADE)
    subgroup = models.ForeignKey('SubGroup', related_name='group_mapping', on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f"{self.group} - {self.subgroup}"



class Item(models.Model):
    CONSUMABLE_CHOICES = [
        ('Consumable', 'Consumable'),
        ('Non-Consumable', 'Non-Consumable'),
    ]

    CONDITION = [
        ('new', 'New'),
        ('operational', 'Operational'),
        ('damaged', 'Damaged'),
        ('maintained', 'Maintained'),
    ]
    CATEGORY_CHOICES = [
        ('Furniture', 'Furniture'),
        ('Stationery', 'Stationery'),
        ('Machinery', 'Machinery'),
        ('ITC', 'ITC'),
        ('Electronics', 'Electronics'),
        ('Kitchen Items', 'Kitchen Items'),
        ('Sanitary Items', 'Sanitary Items'),
        ('Clothes', 'Clothes'),
        ('Others', 'Others')
    ]

    UNIT_CHOICES = [
    ('Pcs', 'Pcs'),
    ('Dozen', 'Dozen'),
    ('Mtrs', 'Mtrs'),
    ('Feet', 'Feet'),
    ('Kilogram', 'Kilogram'),
    ('Liters', 'Liters'),
    ('Square Meter', 'Square Meter'),
    ('Cubic Meter', 'Cubic Meter'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('none', 'None')
    ]



    name = models.CharField(max_length=100 )
    description = models.CharField(blank=True)
    consumable = models.CharField(max_length=20, choices=CONSUMABLE_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)
    quantity = models.FloatField(default=1.0)  # Change PositiveIntegerField to FloatField

    condition = models.CharField(max_length=20, choices=CONDITION, default='new')  # Set default value to 'new'

    # status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='none', null=True)

    assignedOffice = models.TextField(blank=True)

    assignedBy = models.TextField(blank=True, null = True)

    returnedOffice = models.TextField(blank=True)
    remarks = models.CharField(blank=True, default="Damaged")
    storeDate = models.DateField(blank=True, null=True)

    assignedDateByStore = models.DateField(blank=True, null=True)
    assignedDateByGroup = models.DateField(blank=True, null=True)

    # officeDate = models.DateField(blank=True, null=True)
    damagedDate = models.DateField(blank=True, null=True)
    maintainedDate = models.DateField(blank=True, null=True)
    returnDate = models.DateField(blank=True, null=True)

    additem_photo = models.ImageField(upload_to=item_photo_upload_path, blank=True, null=True)
    changestatus_photo = models.ImageField(upload_to=changestatus_photo_upload_path, blank=True, null=True)
    returnitem_photo = models.ImageField(upload_to=returnitem_photo_upload_path, blank=True, null=True)

    unit = models.CharField(max_length=50, blank=True, null=True, choices=UNIT_CHOICES)
    jinsi_no = models.CharField(max_length=100, unique=True, null=True, blank=True)

# ForeignKey to SubGroup
    subgroup = models.ForeignKey(SubGroup, related_name='items', on_delete=models.CASCADE, blank=True, null=True)

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('assign_item', 'Assign Item'),
        ('assign_item_store', 'Assign Item Store'),


        ('return_item', 'Return Item'),
        ('change_status', 'Change Status'),
        ('request_item', 'Request Item'),
        ('add_item', 'Add Item'),
        ('none', 'None')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES,default='none')
    related_object_id = models.PositiveIntegerField(null=True, blank=True)  # Add this field


    def __str__(self):
        return f'{self.notification_type} - {self.title}'



from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# class AssignmentConfirmation(models.Model):
#     item = models.ForeignKey('Item', on_delete=models.CASCADE)
#     assigned_to = models.ForeignKey('SubGroup', on_delete=models.CASCADE)
#     quantity = models.FloatField()
#     confirmed = models.BooleanField(default=False)
#     confirmation_date = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     ####
#     assigned_office = models.CharField(max_length=255,null=True)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='item_confirmations',null=True)



#     def __str__(self):
#         return f'Confirmation for {self.item.name} to {self.assigned_to.name}'

class AssignConfirmation(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    assigned_office = models.CharField(max_length=255,null=True, blank=True)

    assigned_to = models.ForeignKey('SubGroup', on_delete=models.CASCADE,null=True, blank=True)
    quantity = models.FloatField()
    confirmed = models.BooleanField(default=False)
    confirmation_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_office = models.CharField(max_length=255, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='item_confirmations', null=True)

    def __str__(self):
        return f'Confirmation for {self.item.name} to {self.assigned_to.name}'

# class AssignConfirmationStore(models.Model):
#     item = models.ForeignKey('Item', on_delete=models.CASCADE)
#     assigned_to = models.CharField(max_length=255)
#     quantity = models.FloatField()
#     confirmed = models.BooleanField(default=False)
#     confirmation_date = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     assigned_office = models.CharField(max_length=255, null=True)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='item_confirmations', null=True)

#     def __str__(self):
#         return f'Confirmation for {self.item.name} to {self.assigned_to.name}'

class PendingItem(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    assigned_office = models.CharField(max_length=255)
    quantity = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    confirmation_requested = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f'Pending Item {self.item.name} for {self.assigned_office}'



# class ItemRequest(models.Model):

#     UNIT_CHOICES = [
#     ('Pcs', 'Pcs'),
#     ('Dozen', 'Dozen'),
#     ('Mtrs', 'Mtrs'),
#     ('Feet', 'Feet'),
#     ('Kilogram', 'Kilogram'),
#     ('Liters', 'Liters'),
#     ('Square Meter', 'Square Meter'),
#     ('Cubic Meter', 'Cubic Meter'),
# ]
   
#     item_name = models.CharField(max_length=255)

#     FIXED_KEYS = ["subgroup", "group", "officer", "under_secretary", "joint_secretary"]

#     item_quantity = models.JSONField(default=dict)

#     unit = models.CharField(max_length=50, blank=True, null=True, choices=UNIT_CHOICES)

#     requested_group = models.CharField(max_length=255,null=True)

#     requested_subgroup = models.CharField(max_length=255,null=True)

#     description = models.CharField(blank=True, null=True)

#     requestitem_photo = models.ImageField(upload_to=requestitem_photo_upload_path, blank=True, null=True)


#     dates = models.JSONField(default=dict)

#     STATUS_CHOICES = ["requested", "forwarded", "edited_forwarded", "rejected", "accepted"]

#     status = models.JSONField(default=dict)

#     def clean(self):
#         """
#         Custom validation to ensure item_quantity, dates, and status dictionaries have fixed keys 
#         and status values are within the defined STATUS_CHOICES.
#         """
#         # Validate item_quantity keys
#         for key in self.item_quantity.keys():
#             if key not in self.FIXED_KEYS:
#                 raise ValidationError(_(f"Invalid key '{key}' in item_quantity. Allowed keys are {', '.join(self.FIXED_KEYS)}."))

#         # Validate dates keys
#         for key in self.dates.keys():
#             if key not in self.FIXED_KEYS:
#                 raise ValidationError(_(f"Invalid key '{key}' in dates. Allowed keys are {', '.join(self.FIXED_KEYS)}."))

#         # Validate status keys and values
#         for key, value in self.status.items():
#             if key not in self.FIXED_KEYS:
#                 raise ValidationError(_(f"Invalid key '{key}' in status. Allowed keys are {', '.join(self.FIXED_KEYS)}."))
#             if value not in self.STATUS_CHOICES:
#                 raise ValidationError(_(f"Invalid status '{value}' for {key}. Allowed values are {', '.join(self.STATUS_CHOICES)}."))

#     def __str__(self):
#         """
#         String representation of the model instance.
#         """
#         return self.item_name

 
 
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class ItemRequest(models.Model):
    UNIT_CHOICES = [
        ('Pcs', 'Pcs'),
        ('Dozen', 'Dozen'),
        ('Mtrs', 'Mtrs'),
        ('Feet', 'Feet'),
        ('Kilogram', 'Kilogram'),
        ('Liters', 'Liters'),
        ('Square Meter', 'Square Meter'),
        ('Cubic Meter', 'Cubic Meter'),
    ]

    AVAILABLE_CHOICES = [
        ('Stock', 'Stock'),
        ('Buy', 'Buy'),
        ('Others','Others'),
    ]

    FIXED_KEYS = ["subgroup", "group", "officer", "under_secretary", "joint_secretary"]
    STATUS_CHOICES = ["requested", "forwarded", "edited_forwarded", "edited_accepted", "rejected", "accepted", ""]

    item_name = models.CharField(max_length=255)
    item_quantity = models.JSONField(default=dict)
    unit = models.CharField(max_length=50, blank=True, null=True, choices=UNIT_CHOICES)
    available = models.CharField(max_length=50, choices=AVAILABLE_CHOICES, blank=True, null=True)
    available_description = models.CharField(max_length=255, null=True)

    requested_group = models.CharField(max_length=255, null=True)
    requested_subgroup = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    requestitem_photo = models.ImageField(upload_to=requestitem_photo_upload_path, blank=True, null=True)
    dates = models.JSONField(default=dict)
    status = models.JSONField(default=dict)

    def clean(self):
        """
        Custom validation to ensure item_quantity, dates, and status dictionaries have fixed keys 
        and status values are within the defined STATUS_CHOICES.
        """
        # Validate item_quantity keys
        for key in self.item_quantity.keys():
            if key not in self.FIXED_KEYS:
                raise ValidationError(_(f"Invalid key '{key}' in item_quantity. Allowed keys are {', '.join(self.FIXED_KEYS)}."))

        # Validate dates keys
        for key in self.dates.keys():
            if key not in self.FIXED_KEYS:
                raise ValidationError(_(f"Invalid key '{key}' in dates. Allowed keys are {', '.join(self.FIXED_KEYS)}."))

        # Validate status keys and values
        for key, value in self.status.items():
            if key not in self.FIXED_KEYS:
                raise ValidationError(_(f"Invalid key '{key}' in status. Allowed keys are {', '.join(self.FIXED_KEYS)}."))

            if value not in self.STATUS_CHOICES:
                raise ValidationError(_(f"Invalid status '{value}' for {key}. Allowed values are {', '.join(self.STATUS_CHOICES)}."))

    def __str__(self):
        """
        String representation of the model instance.
        """
        return self.item_name

 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 # log = models.TextField(blank=True, null=True)

    # def update_log(self, action, office):
    #     log_entry = {
    #         'action': action,
    #         'office': office,
    #         'date': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    #     }

    #     if self.log:
    #         logs = json.loads(self.log)
    #         logs.append(log_entry)
    #     else:
    #         logs = [log_entry]

    #     self.log = json.dumps(logs)
    #     self.save()



    # def __str__(self):
    #     return self.name