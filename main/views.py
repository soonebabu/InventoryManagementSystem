from django.shortcuts import render,redirect
from django.template.loader import get_template
from django.core import serializers
from django.http import JsonResponse
from django.db.models import Count, Q, Sum
from . import models
from . import forms
import stripe
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.models import Group
from datetime import timedelta
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError  
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models.functions import TruncDay, TruncMonth
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet
import json
from .forms import SignUp
from .models import SubGroup
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import Group, User
from . import models, forms

# FAQ
def faq_list(request):
	faq=models.Faq.objects.all()
	return render(request, 'faq.html',{'faqs':faq})

# Contact
def contact_page(request):
	return render(request, 'contact_us.html')


#Add Group
@login_required

def add_group(request):
    if request.method == 'POST':
        form = forms.GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('group_list')  # Redirect to a view displaying all groups
    else:
        form = forms.GroupForm()
    return render(request, 'groups/add_group.html', {'form': form})

#Group List

def group_list(request):
    groups = Group.objects.all()  
    return render(request, 'groups/group_list.html', {'groups': groups})

from django.contrib.auth.models import Group as AuthGroup

@login_required
def delete_group(request, group_id):
    group = get_object_or_404(AuthGroup, pk=group_id)
    
    # Retrieve all subgroups associated with the group
    subgroups = group.subgroups.all()
    
    # Remove entries from GroupSubgroupMapping for the group's subgroups
    models.GroupSubgroupMapping.objects.filter(subgroup__in=subgroups).delete()
    
    # Remove each subgroup and its associated users
    for subgroup in subgroups:
        # Remove associated users
        users = subgroup.users.all()
        for user in users:
            user.groups.remove(group)
            user.save()
        
        # Delete the subgroup
        subgroup.delete()
    
    # Delete the group
    group.delete()
    
    return redirect('group_list')

#Add Subgroup
def add_subgroup(request):
    if request.method == 'POST':
        form = forms.SubGroupForm(request.POST)
        if form.is_valid():
            subgroup = form.save(commit=False)  # Save the subgroup instance but don't commit it yet
            subgroup.save()  # Now save the subgroup instance
            # Create a new GroupSubgroupMapping instance for the subgroup and its group
            models.GroupSubgroupMapping.objects.create(group=subgroup.parent_group, subgroup=subgroup)
            return redirect('subgroup_list')  # Assuming you have a view named subgroup_list
    else:
        form = forms.SubGroupForm()

    return render(request, 'groups/add_subgroup.html', {'form': form})


#Sub Group List
def subgroup_list(request):
    subgroups = SubGroup.objects.all()
    return render(request, 'groups/subgroup_list.html', {'subgroups': subgroups})

def delete_subgroup(request, subgroup_id):
    subgroup = get_object_or_404(SubGroup, pk=subgroup_id)
    
    # Remove associated users
    subgroup.users.clear()
    
    # Remove subgroup from group subgroup mapping
    models.GroupSubgroupMapping.objects.filter(subgroup=subgroup).delete()
    
    # Delete the subgroup
    subgroup.delete()
    
    return redirect('subgroup_list')


#Update SUPERADMIN Profile
@login_required
def update_profile(request):
    msg = None

    if request.method == 'POST':
        form = forms.CustomProfileForm(request.POST, instance=request.user, request=request)
        if form.is_valid():
            form.save()
            msg = 'Data has been saved'
    else:
        form = forms.CustomProfileForm(instance=request.user, request=request)

    return render(request, 'user/update-profile.html', {'form': form, 'msg': msg})

#Update Other User Profile
@login_required
def update_user_profile(request):
    msg = None

    # Check if the logged-in user is in the 'SUPERADMIN' group
    if not request.user.groups.filter(name='SUPERADMIN').exists():
        return render(request, 'contact_us.html')

    if request.method == 'POST':
        form = forms.UserUpdateForm(request.POST)
        if form.is_valid():
            user_to_update = form.cleaned_data['user_to_update']

            # Update only the fields that have changed
            for field in form.Meta.fields:
                if field != 'username' and form.cleaned_data[field] is not None:
                    setattr(user_to_update, field, form.cleaned_data[field])

            # Save the changes, excluding the username field
            user_to_update.save(update_fields=[field for field in form.Meta.fields if field != 'username'])
            msg = 'User profile updated successfully'
        else:
            print(form.errors)

    else:
        form = forms.UserUpdateForm()

    return render(request, 'user/update-user-profile.html', {'form': form, 'msg': msg})

def cancel_update(request):
    # Redirect to the desired URL when the cancel button is clicked
    return redirect('user/update-user-profile.html')

#Reset Other User Profile
@login_required
def reset_user_password(request):
    # Check if the logged-in user is in the 'SUPERADMIN' group
    if not request.user.groups.filter(name='SUPERADMIN').exists():
        return render(request, 'contact_us.html')

    msg = None

    if request.method == 'POST':
        form = forms.ResetPasswordForm(request.POST)
        if form.is_valid():
            form.save()
            msg = 'Password reset successfully'

    else:
        form = forms.ResetPasswordForm()

    return render(request, 'user/reset-password.html', {'form': form, 'msg': msg})

def get_user_data(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        user_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'username': user.username
            # Add other fields as needed
        }
        return JsonResponse(user_data)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

#User List
def user_list(request):
    if request.user.groups.filter(name='SUPERADMIN').exists():
        # Get all users
        users = User.objects.all()
        context = {'users': users}
        return render(request, 'user_list.html', context)
    else:
        return None



#Home Page
@login_required
def home(request):
    return render(request, 'home.html')

# home view
# @login_required

# def home(request):
#     user_groups = request.user.groups.values_list('name', flat=True)
#     user_subgroups = models.SubGroup.objects.filter(users=request.user)
#     assigned_offices = []

#     if 'SUPERADMIN' in user_groups:
#         assigned_offices = models.Item.objects.values_list('assignedOffice', flat=True).distinct()
#     elif user_subgroups.exists():
#         subgroup_names = user_subgroups.values_list('name', flat=True)   
#         assigned_offices = subgroup_names
#     elif user_groups.exists():
#         user_group = user_groups.first()
#         subgroups = models.GroupSubgroupMapping.objects.filter(group__name=user_group).values_list('subgroup__name', flat=True)
#         assigned_offices = [user_group] + list(subgroups)

#     # Calculate count values for condition labels
#     condition_labels = ['new', 'operational', 'damaged', 'maintained']
#     condition_counts = {}

#     for office in assigned_offices:
#         for condition in condition_labels:
#             count = models.Item.objects.filter(assignedOffice=office, condition=condition).count()
#             condition_counts.setdefault(condition, []).append(count)

#     # Calculate day-wise data for line chart
#     line_chart_data = {}
#     for office in assigned_offices:
#         line_chart_data[office] = get_day_wise_data(user_groups, office)
#         # print('line_chart_data', line_chart_data)

#     # Prepare data for the pie chart (monthly basis)
#     pie_chart_data = {}
#     for office in assigned_offices:
#         monthly_counts = [0] * 12
#         for month in range(1, 13):
#             count = models.Item.objects.filter(assignedOffice=office, officeDate__month=month).count()
#             monthly_counts[month - 1] = count
#         pie_chart_data[office] = monthly_counts
#         # print('pie_chart_data', pie_chart_data)

#     context = {
#         'assigned_offices': assigned_offices,
#         'condition_labels': condition_labels,
#         'condition_counts': condition_counts,
#         'line_chart_data': line_chart_data,
#         'pie_chart_data': pie_chart_data,
#     }

#     return render(request, 'home.html', context)

# def get_day_wise_data(user_groups, user_group_name):
#     end_date = datetime.now()
#     start_date = end_date - timedelta(days=30)

#     if 'SUPERADMIN' in user_groups:
#         queryset = models.Item.objects.filter(officeDate__range=[start_date, end_date])
#     else:
#         if user_groups:
#             associated_offices = models.SubGroup.objects.filter(parent_group__name=user_group_name).values_list('name', flat=True)
#         else:
#             associated_offices = []

#         if associated_offices:
#             queryset = models.Item.objects.filter(assignedOffice__in=associated_offices, officeDate__range=[start_date, end_date])
#         else:
#             queryset = models.Item.objects.filter(assignedOffice=user_group_name, officeDate__range=[start_date, end_date])

#     day_wise_data = (
#         queryset
#         .annotate(month=TruncMonth('officeDate'))
#         .values('month')
#         .annotate(count=Count('id'))
#         .order_by('month')
#     )

#     day_wise_data_list = [
#         {'month': entry['month'].strftime('%Y-%m'), 'count': entry['count']}
#         for entry in day_wise_data
#     ]
#     # print('day_wise_data_list', day_wise_data_list)

#     return day_wise_data_list


   


#Create User
@login_required

def signup(request):
    msg = None

    if request.method == 'POST':
        form = SignUp(request.POST)
        print(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            group_name = form.cleaned_data['group']
            user_group = Group.objects.get(name=group_name)
            user.save()
            user.groups.add(user_group)
            subgroup_name = form.cleaned_data.get('subgroup')
            if subgroup_name:
                subgroup = models.SubGroup.objects.get(name=subgroup_name, parent_group=user_group)
                print("subgroup", subgroup)
                subgroup.users.add(user)
                print("User added to subgroup:", user, subgroup)
            else:
                print("User not added to any subgroup:", user)

            print("User registered:", user)
            msg = 'Thank you for registering.'
            return redirect('user_list')
    else:
        form = SignUp()

    return render(request, 'registration/signup.html', {'form': form, 'msg': msg})

from django.views.decorators.http import require_POST

@require_POST
def delete_user(request, user_id):
    # Retrieve the user
    user = get_object_or_404(User, pk=user_id)
    
    # Delete the user
    user.delete()
    
    return redirect('user_list')  # Redirect to the user list page after deletion


def fetch_subgroups(request):
    selected_group_id = request.GET.get('group')
    print(f"Selected Group ID: {selected_group_id}")  # Debug
    subgroups = SubGroup.objects.filter(parent_group_id=selected_group_id)
    data = [{'id': subgroup.id, 'name': subgroup.name} for subgroup in subgroups]
    return JsonResponse(data, safe=False)



# Login
def login(request):
    if request.method == 'POST':
        form = forms.LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  # Log the user in

            return redirect('home')  # Redirect to the user's profile or any other desired page

    else:
        form = forms.LoginForm()

    return render(request, 'registration/login.html', {'form': form,})


from django.utils import timezone


#Edit Item
def edit_item(request, item_id):
    item = get_object_or_404(models.Item, pk=item_id)

    if request.method == 'POST':
        form = forms.ItemForm(request.POST, instance=item)
        print(request.POST)
        print('*******PRINT item', item.assignedOffice)
        if form.is_valid():
            print("*****before assinging value ", form.instance.__dict__)
            form.instance.assignedOffice = item.assignedOffice
            print("******after assinging value ", form.instance.__dict__)

            form.save()
            return redirect('item_list')
    else:
        form = forms.ItemForm(instance=item)
    return render(request, 'inventory/add_item.html', {'form': form, 'item': item})


# def add_item_for_store(request, allowed_groups):
#     if request.method == 'POST':
#         form = forms.ItemForm(request.POST, request.FILES)
#         if form.is_valid():
#             item = form.save(commit=False)
#             user_group = request.user.groups.first()
#             item.assignedOffice = user_group.name

#             ######
#             if user_group.name == 'FSCMO':
#                 # If the user is a FSCMO, allow selecting the office
#                 assigned_office = request.POST.get('assigned_office')  # Assuming there's a field in the form for this
#             else:
#                 # For other users, assign the item to their own office
#                 assigned_office = user_group.name


#             ######

#             # Check if the item is non-consumable and has quantity greater than 1
#             if item.consumable == 'Non-Consumable' and item.quantity > 1:
#                 # If it's non-consumable and quantity > 1, show an error message
#                 form.add_error('quantity', 'Quantity must be 1 for non-consumable items.')
#                 # Re-render the form with the error message
#                 return render(request, 'inventory/add_item.html', {'form': form, 'allowed_groups': allowed_groups})
        
#             else:
#                 item.save()
#                 # Update storeDate for the added item
#                 item.storeDate = timezone.now()
#                 item.save()

#             return redirect('item_list')
#     else:
#         form = forms.ItemForm()

#     return render(request, 'inventory/add_item.html', {'form': form, 'allowed_groups': allowed_groups})


#############FUNCTION TO ADD ITEMS TO GROUPS AND SUBGROUPS WITHOUT CONFIRMATION
#Add Item
# @login_required
# def add_item(request):
#     user_groups = request.user.groups.all()
#     allowed_groups = [group.name for group in Group.objects.all()]

#     user_belongs_to_group = any(group.name in allowed_groups for group in user_groups)

#     if user_belongs_to_group:
#         return add_item_for_store(request, allowed_groups)
#     else:
#         # User does not belong to allowed groups, handle accordingly (redirect, error message, etc.)
#         return HttpResponse("You are not authorized to add items.")



# @login_required
# def add_item_for_store(request, allowed_groups):
#     groups = Group.objects.exclude(name__in=['SUPERADMIN', 'FSCMO'])
#     subgroups = SubGroup.objects.all()
    
#     if request.method == 'POST':
#         form = forms.ItemForm(request.POST, request.FILES)
#         if form.is_valid():
#             item = form.save(commit=False)
#             user_group = request.user.groups.first()
            
#             if user_group.name == 'FSCMO':
#                 # Allow FSCMO to select the office (group or subgroup)
#                 assigned_office = request.POST.get('assigned_office')
#             else:
#                 # For other users, assign the item to their own office
#                 assigned_office = user_group.name

#             item.assignedOffice = assigned_office

#             # Check if the item is non-consumable and has quantity greater than 1
#             if item.consumable == 'Non-Consumable' and item.quantity > 1:
#                 form.add_error('quantity', 'Quantity must be 1 for non-consumable items.')
#                 return render(request, 'inventory/add_item.html', {'form': form, 'allowed_groups': allowed_groups, 'groups': groups, 'subgroups': subgroups})

#             item.storeDate = timezone.now()
#             item.save()
#             return redirect('item_list')
#     else:
#         form = forms.ItemForm()

#     return render(request, 'inventory/add_item.html', {'form': form, 'allowed_groups': allowed_groups, 'groups': groups, 'subgroups': subgroups})



#############FUNCTION FOR ADDING ITEM TO GROUPS AND SUBGROUPS ONLY AFTER CONFIRMATION
# @login_required
# def add_item(request):
#     user_groups = request.user.groups.all()
#     allowed_groups = [group.name for group in Group.objects.all()]

#     user_belongs_to_group = any(group.name in allowed_groups for group in user_groups)

#     if user_belongs_to_group:
#         return add_item_for_store(request, allowed_groups)
#     else:
#         return HttpResponse("You are not authorized to add items.")

# ## views.py



# @login_required
# def add_item_for_store(request, allowed_groups):
#     groups = Group.objects.exclude(name__in=['SUPERADMIN', 'FSCMO', 'OFFICER', 'UNDERSECRETARY', 'JOINTSECRETARY'])
#     subgroups = models.SubGroup.objects.all()

#     if request.method == 'POST':
#         form = forms.ItemForm(request.POST, request.FILES)
#         if form.is_valid():
#             item = form.save(commit=False)  # Save the form but don't commit to the database yet
#             user_group = request.user.groups.first()

#             if user_group.name == 'FSCMO':
#                 assigned_office = request.POST.get('assigned_office')
#             else:
#                 assigned_office = user_group.name

#             if item.consumable == 'Non-Consumable' and item.quantity > 1:
#                 form.add_error('quantity', 'Quantity must be 1 for non-consumable items.')
#                 return render(request, 'inventory/add_item.html', {'form': form, 'allowed_groups': allowed_groups, 'groups': groups, 'subgroups': subgroups})

#             item.assignedOffice = assigned_office
#             item.status = 'pending'  # Explicitly set the status field
#             item.storeDate = timezone.now()
#             item.save()  # Save the item to the database

#             # Create a PendingItem for confirmation
#             pending_item = models.PendingItem(
#                 item=item,
#                 assigned_office=assigned_office,
#                 quantity=item.quantity,
#                 created_by=request.user,
#                 is_confirmed=False
#             )
#             pending_item.save()  # Now save the pending item

#             # Notification logic
#             # if assigned_office in [group.name for group in groups]:
#             #     assigned_group = get_object_or_404(Group, name=assigned_office)
#             #     users_in_group = User.objects.filter(groups=assigned_group)
#             # else:
#             #     assigned_subgroup = get_object_or_404(models.SubGroup, name=assigned_office)
#             #     users_in_group = User.objects.filter(subgroups=assigned_subgroup)
#             # print('users_in_group',users_in_group)

#             # Notification logic
#             users_in_group = User.objects.none()
#             if Group.objects.filter(name=assigned_office).exists():
#                 assigned_group = get_object_or_404(Group, name=assigned_office)
#                 subgroups_of_group = models.SubGroup.objects.filter(parent_group=assigned_group)

#                 print('assigned_group', assigned_group)
#                 users_in_group = User.objects.filter(groups=assigned_group).exclude(subgroups__in=subgroups_of_group).distinct()
#                 print('users_in_group inside loop', users_in_group)
#             elif models.SubGroup.objects.filter(name=assigned_office).exists():
#                 assigned_subgroup = get_object_or_404(models.SubGroup, name=assigned_office)
#                 users_in_group = User.objects.filter(subgroups=assigned_subgroup)

#             print('users_in_group', users_in_group)

#             for user in users_in_group:
#                 models.Notification.objects.create(
#                     user=user,
#                     title=f'Confirmation needed: {item.name} add',
#                     message=f'Please confirm the addition of {item.name}.',
#                     notification_type='add_item',
#                     related_object_id=pending_item.id  # Assuming Notification model has a related_object_id field
#                 )

#             return redirect('item_list')
#         else:
#             # If form is not valid, print form errors for debugging
#             print(form.errors)
#     else:
#         form = forms.ItemForm()

#     return render(request, 'inventory/add_item.html', {'form': form, 'allowed_groups': allowed_groups, 'groups': groups, 'subgroups': subgroups})

# @login_required
# def confirm_item(request, pending_item_id):
#     pending_item = get_object_or_404(models.PendingItem, id=pending_item_id)
#     if request.method == 'POST':
#         if 'confirm' in request.POST:
#             # Move the item from pending to confirmed
#             item = pending_item.item
#             item.assignedOffice = pending_item.assigned_office
#             item.quantity = pending_item.quantity
#             item.storeDate = timezone.now()
#             item.status = 'confirmed'
#             item.save()  # Save the item to the inventory with confirmed status
#             pending_item.delete()  # Delete the pending item
#             return redirect('item_list')
#         elif 'reject' in request.POST:
#             # Change item status to rejected and then delete pending item
#             item = pending_item.item
#             item.status = 'rejected'
#             item.save()
#             pending_item.delete()  # Delete the pending item
#             return redirect('item_list')
#     return render(request, 'inventory/notifications/confirm_item_addition.html', {'pending_item': pending_item})

################FUNCTION TO ADD ITEMS TO FSCMO

import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import IntegrityError
from .models import Item
from .forms import UploadFileForm

@login_required
def bulk_add_items(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            df = pd.read_excel(file)

            for index, row in df.iterrows():
                item_data = {
                    'name': row['name'],
                    'description': row['description'],
                    'consumable': row['consumable'],
                    'category': row['category'],
                    'quantity': row['quantity'],  # This will be used to create multiple entries if necessary
                    'unit': row['unit'],
                    'condition': 'new',
                    'assignedOffice': request.user.groups.filter(name='FSCMO').first().name
                }
                # Handle optional fields
                item_data['additem_photo'] = row.get('additem_photo', None)
                
                if row['consumable'] == 'Non-Consumable':
                    item_data['jinsi_no'] = row.get('jinsi_no', None)
                else:
                    item_data['jinsi_no'] = None

                # Check if the item is non-consumable and has quantity greater than 1
                if row['consumable'] == 'Non-Consumable' and row['quantity'] > 1:
                    for _ in range(int(row['quantity'])):
                        new_item = Item(**item_data)
                        try:
                            new_item.save()
                            new_item.storeDate = timezone.now()
                            new_item.save()
                        except IntegrityError:
                            # Handle duplicate jinsi_no error
                            continue
                else:
                    item = Item(**item_data)
                    try:
                        item.save()
                        item.storeDate = timezone.now()
                        item.save()
                    except IntegrityError:
                        # Handle duplicate jinsi_no error
                        continue

            return redirect('item_list')
    else:
        form = UploadFileForm()

    return render(request, 'inventory/bulk_add_items.html', {'form': form})




@login_required
def add_item(request):
    # Check if the user belongs to the FSCMO group
    if request.user.groups.filter(name='FSCMO').exists():
        return add_item_for_store(request)
    else:
        # User does not belong to the FSCMO group, handle accordingly (redirect, error message, etc.)
        return HttpResponse("You are not authorized to add items.")

def add_item_for_store(request):
    if request.method == 'POST':
        form = forms.ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            user_group = request.user.groups.filter(name='FSCMO').first()
            item.assignedOffice = user_group.name

            # Check if the item is non-consumable and has quantity greater than 1
            if item.consumable == 'Non-Consumable' and item.quantity > 1:
                # Create separate entries for each quantity
                for _ in range(item.quantity):
                    new_item = models.Item.objects.create(
                        name=item.name,
                        description=item.description,
                        consumable=item.consumable,
                        quantity=1,  # Set quantity to 1 for each entry
                        condition=item.condition,
                        category=item.category,
                        additem_photo=item.additem_photo,
                        assignedOffice=item.assignedOffice  # Set assigned_office for each entry
                    )
                    # Update storeDate for the new item
                    new_item.storeDate = timezone.now()
                    new_item.save()
            else:
                item.save()
                # Update storeDate for the added item
                item.storeDate = timezone.now()
                item.save()

            return redirect('item_list')
    else:
        form = forms.ItemForm()

    return render(request, 'inventory/add_item.html', {'form': form})


            
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.models import Group
from . import models

@login_required
def assign_item_by_store(request):
    # Check if the user belongs to the FSCMO group
    if not request.user.groups.filter(name='FSCMO').exists():
        return HttpResponse("You are not authorized to assign items.")

    groups = Group.objects.exclude(name__in=['SUPERADMIN', 'FSCMO', 'OFFICER', 'UNDERSECRETARY', 'JOINTSECRETARY'])
    subgroups = models.SubGroup.objects.all()

    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')
        assigned_office = request.POST.get('assigned_office')
        print('assigned_office',assigned_office)

        if not assigned_office:
            messages.error(request, 'Assigned office is required.')
            return redirect('assign_item_by_store')

        for item_id in selected_items:
            original_item = get_object_or_404(models.Item, pk=item_id)
            selected_quantity_key = f'selected_quantity_{item_id}'
            new_assigned_to_quantity = int(request.POST.get(selected_quantity_key, 0))

            # Create an AssignConfirmation instance
            confirmation = models.AssignConfirmation.objects.create(
                item=original_item,
                assigned_office=assigned_office,
                
                quantity=new_assigned_to_quantity
            )

            # Notify users in the assigned office (group first, excluding subgroup users, then subgroup users)
            users_in_office = set()
            try:
                assigned_group = Group.objects.get(name=assigned_office)
                subgroup_users = models.SubGroup.objects.filter(parent_group=assigned_group).values_list('users', flat=True)
                group_users = assigned_group.user_set.exclude(id__in=subgroup_users)
                users_in_office.update(group_users)
            except Group.DoesNotExist:
                messages.error(request, 'Assigned group does not exist.')

            try:
                assigned_subgroup = models.SubGroup.objects.get(name=assigned_office)
                subgroup_users = assigned_subgroup.users.all()
                print('subgroup_users',subgroup_users)
                users_in_office.update(subgroup_users)
            except models.SubGroup.DoesNotExist:
                pass  # Subgroup might not exist, which is okay.
                print('users_in_office',users_in_office)

            for user in users_in_office:
                models.Notification.objects.create(
                    user=user,
                    title=f'Confirmation needed: {original_item.name} assignment',
                    message=f'Please confirm the assignment of {original_item.name}.',
                    notification_type='assign_item_store',
                    related_object_id=confirmation.id  # Assuming Notification model has a related_object_id field
                )

        messages.success(request, 'Assignment confirmation requests sent successfully!')
        return redirect('assign_item_by_store')

    else:
        items = models.Item.objects.filter(assignedOffice='FSCMO')
        return render(request, 'inventory/assign_item_by_store.html', {'items': items, 'groups': groups, 'subgroups': subgroups})

@login_required
def confirm_assignment_for_store(request, confirmation_id):
    # Check if the user belongs to the confirmation's assigned office
    confirmation = get_object_or_404(models.AssignConfirmation, id=confirmation_id)
    assigned_office = confirmation.assigned_office

    # Check if the user is part of the assigned office group or subgroup
    user_in_office = False
    try:
        assigned_group = Group.objects.get(name=assigned_office)
        if request.user in assigned_group.user_set.all():
            user_in_office = True
    except Group.DoesNotExist:
        pass

    try:
        assigned_subgroup = models.SubGroup.objects.get(name=assigned_office)
        if request.user in assigned_subgroup.users.all():
            user_in_office = True
    except models.SubGroup.DoesNotExist:
        pass

    if not user_in_office:
        return HttpResponse("You are not authorized to confirm this assignment.")

    if request.method == 'POST':
        confirmed = request.POST.get('confirm', 'no') == 'yes'
        
        if confirmed:
            confirmation.confirmed = True
            confirmation.confirmation_date = timezone.now()
            confirmation.save()

            original_item = confirmation.item
            assigned_office = confirmation.assigned_office
            assigned_quantity = confirmation.quantity

            if original_item.consumable == 'Non-Consumable':
                # Transfer the entire item to the new office
                original_item.assignedOffice = assigned_office
                original_item.quantity = assigned_quantity
                original_item.assignedBy = 'FSCMO'
                original_item.assignedDateByStore = timezone.now()
                original_item.save()
            else:
                # Handle consumable items logic
                if original_item.quantity >= assigned_quantity:
                    new_store_quantity = original_item.quantity - assigned_quantity

                    # Update quantity for the original office
                    original_item.quantity = new_store_quantity
                    original_item.save()

                    # Create a new item for the destination office
                    models.Item.objects.create(
                        name=original_item.name,
                        jinsi_no=original_item.jinsi_no,  # Transfer the jinsi_no
                        description=original_item.description,
                        consumable=original_item.consumable,
                        quantity=assigned_quantity,
                        unit=original_item.unit,
                        condition=original_item.condition,
                        category=original_item.category,
                        assignedOffice=assigned_office,
                        storeDate=original_item.storeDate,
                        assignedBy = 'FSCMO',
                        assignedDateByStore=timezone.now()
                    )
                else:
                    messages.error(request, 'Assigned quantity exceeds available quantity.')

            messages.success(request, 'Item assignment confirmed successfully!')
        else:
            # Reassign the items back to FSCMO
            confirmation.item.assignedOffice = 'FSCMO'
            confirmation.item.save()
            messages.info(request, 'Item assignment not confirmed and reassigned to FSCMO.')

        return redirect('view_notifications')

    return render(request, 'inventory/notifications/confirm_assignment.html', {'confirmation': confirmation})



@login_required
def pending_items_list(request):
    pending_items = models.PendingItem.objects.filter(is_confirmed=False)
    return render(request, 'inventory/pending_items_list.html', {'pending_items': pending_items})


def get_user_group_name(user):
    return user.groups.first().name if user.groups.exists() else None


#Item List

@login_required
def item_list(request):
    # Get the user's groups and subgroups
    user_groups = request.user.groups.values_list('name', flat=True)
    print(user_groups)

    # Initialize assigned_offices list
    assigned_offices = []

    if 'SUPERADMIN' in user_groups or 'FSCMO' in user_groups or 'OFFICER' in user_groups or 'UNDERSECRETARY' in user_groups or 'JOINTSECRETARY' in user_groups:
        # Fetch all items
        items = models.Item.objects.all()
        print('items', items)

        # If user belongs to both 'SUPERADMIN' and 'FSCMO', 
        # assign all office names to assigned_offices
        if 'SUPERADMIN' in user_groups or 'FSCMO' in user_groups:
            assigned_offices.extend(models.Item.objects.values_list('assignedOffice', flat=True).distinct())
            print('assigned_offices',assigned_offices)

    else:
        user_subgroups = models.SubGroup.objects.filter(users=request.user)

        if user_subgroups.exists():  # If the user belongs to any subgroups
            subgroup_names = user_subgroups.values_list('name', flat=True) 
            items = models.Item.objects.filter(assignedOffice__in=subgroup_names)
  
            # items = models.Item.objects.filter(assignedOffice__in=subgroup_names, status__in=['pending', 'confirmed'])
            assigned_offices.extend(subgroup_names)

        elif user_groups.exists():  # If the user belongs to any groups (excluding SUPERADMIN and FSCMO)
            user_group = user_groups.first()
            subgroups = models.GroupSubgroupMapping.objects.filter(group__name=user_group).values_list('subgroup__name', flat=True)
            items = models.Item.objects.filter(assignedOffice__in=[user_group] + list(subgroups))

            # items = models.Item.objects.filter(assignedOffice__in=[user_group] + list(subgroups), status__in=['pending', 'confirmed'])
            assigned_offices.extend([user_group] + list(subgroups))

        else:
            items = models.Item.objects.none()

    

    unread_notification_count = models.Notification.objects.filter(user=request.user, is_read=False).count() 
    return render(request, 'inventory/item_list.html', {'items': items, 'unread_notification_count': unread_notification_count,'assigned_offices':assigned_offices, 'user_groups': user_groups})



@login_required
def delete_item(request, item_id):
    user_groups = request.user.groups.values_list('name', flat=True)
    if 'FSCMO' in user_groups:

        item = get_object_or_404(models.Item, id=item_id)
        item.delete()
    return redirect('item_list')

#Photo List
def photo_list(request, item_pk):
    item = get_object_or_404(models.Item, pk=item_pk)
    context = {
        'item': item,
    }
    return render(request, 'inventory/photo_list.html', context)


#Filter Item
@login_required

def filter_items(request):
    # Get the user's group names
    user_group_names = [group.name for group in request.user.groups.all()]
    allowed_offices = []

    if 'SUPERADMIN' or 'FSCMO'  or 'OFFICER' or 'UNDERSECRETARY' or 'JOINTSECRETARY' in user_group_names:
        allowed_offices = Item.objects.values_list('assignedOffice', flat=True).distinct()
        print('allowed_offices',allowed_offices)
    else:
        user_subgroup = SubGroup.objects.filter(users=request.user).first()
        if user_subgroup:
            allowed_offices = [user_subgroup.name]
        else:
            user_subgroups = SubGroup.objects.filter(parent_group__name__in=user_group_names)
            if user_subgroups.exists():
                user_group_names.extend([subgroup.name for subgroup in user_subgroups])
            else:
                allowed_offices.extend(user_group_names)

    items = Item.objects.filter(assignedOffice__in=allowed_offices)

    return render(request, 'inventory/filter_form.html', {'items': items})



# views.py
from openpyxl import Workbook
from django.http import HttpResponse
from .models import Item
from django.contrib.auth.decorators import user_passes_test

# Utility function to filter items based on parameters

def get_filtered_items(user, start_date, end_date, assigned_office):
    # Fetch all items initially
    filtered_items = Item.objects.all()

    # Create Q objects for OR logic on multiple date fields
    date_filter = (
        Q(assignedDateByStore__range=[start_date, end_date]) |
        Q(assignedDateByGroup__range=[start_date, end_date]) |
        Q(damagedDate__range=[start_date, end_date]) |
        Q(maintainedDate__range=[start_date, end_date]) |
        Q(returnDate__range=[start_date, end_date])
    )
    # Apply the date filter to the queryset
    filtered_items = filtered_items.filter(date_filter)

    # Check if the user is SUPERADMIN
    if user.groups.filter(Q(name='SUPERADMIN') | Q(name='FSCMO')).exists():
        # If SUPERADMIN, allow all items
        pass
    else:
        # For other users, filter items based on their groups and subgroups
        user_group_names = [group.name for group in user.groups.all()]
        allowed_offices = []

        # Check if the user belongs to any subgroup
        user_subgroups = SubGroup.objects.filter(users=user)
        if user_subgroups.exists():
            # If user belongs to subgroups, filter items for those subgroups only
            allowed_offices.extend(user_subgroups.values_list('name', flat=True))
        else:
            # If user does not belong to any subgroup, filter items for their groups and associated subgroups
            for group_name in user_group_names:
                # Add the parent group itself to the allowed offices
                allowed_offices.append(group_name)
                # Get subgroups for the parent group
                parent_group = Group.objects.get(name=group_name)
                subgroups = parent_group.subgroups.all()
                # Add subgroups to the allowed offices
                allowed_offices.extend(subgroup.name for subgroup in subgroups)

        # Filter items by allowed offices
        filtered_items = filtered_items.filter(assignedOffice__in=allowed_offices)

    # Filter items by assigned office if specified
    if assigned_office:
        filtered_items = filtered_items.filter(assignedOffice__iexact=assigned_office)

    return filtered_items


    

# View to export filtered items to Excel
def export_filtered_to_excel(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    assigned_office = request.GET.get('assigned_office')
    
    filtered_items = get_filtered_items(request.user, start_date, end_date, assigned_office)

    data = {
        'Name': [item.name for item in filtered_items],
        'Jinsi_No': [item.jinsi_no for item in filtered_items],
        'Description': [item.description for item in filtered_items],
        'Consumable': [item.consumable for item in filtered_items],
        'Category' : [item.category for item in filtered_items],
        'Quantity': [item.quantity for item in filtered_items],
        'Unit': [item.unit for item in filtered_items],
        'Condition': [item.get_condition_display() for item in filtered_items],
        'Assigned Office': [item.assignedOffice for item in filtered_items],
        'Store Entered Date': [item.assignedDateByStore for item in filtered_items],
        'Office Assigned Date': [item.assignedDateByGroup for item in filtered_items],
        'Store Returned Date': [item.returnDate for item in filtered_items],
        'Damaged Date': [item.damagedDate for item in filtered_items],
        'Maintained Date': [item.maintainedDate for item in filtered_items],
    }

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    response['Content-Disposition'] = f'attachment; filename="{current_datetime}_filtered_items.xlsx"'


    # response['Content-Disposition'] = 'attachment; filename="filtered_items.xlsx"'
    df.to_excel(response, index=False)

    return response

# Decorator to check user permissions for exporting to Excel


from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group, User
from .models import Item


@login_required
def assign_item(request):
    user_groups = request.user.groups.values_list('name', flat=True)
    print("User Groups:", user_groups)  # Debugging statement

    # Dynamically fetch available subgroups based on user's group
    available_subgroups = []
    for group_name in user_groups:
        parent_group = Group.objects.get(name=group_name)
        subgroups = models.SubGroup.objects.filter(parent_group=parent_group)
        available_subgroups.extend(subgroups.values_list('name', flat=True))

    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')
        assigned_to = request.POST.get('assigned_to')

        for item_id in selected_items:
            original_item = models.Item.objects.get(pk=item_id)
            selected_quantity_key = f'selected_quantity_{item_id}'
            new_assigned_to_quantity = float(request.POST.get(selected_quantity_key, 0))

            # Create an AssignConfirmation instance
            confirmation = models.AssignConfirmation.objects.create(
                item=original_item,
                assigned_to=models.SubGroup.objects.get(name=assigned_to),
                quantity=new_assigned_to_quantity
            )

            # Notify users in the assigned subgroup
            assigned_subgroup = models.SubGroup.objects.get(name=assigned_to)
            for user_in_subgroup in assigned_subgroup.users.all():
                models.Notification.objects.create(
                    user=user_in_subgroup,
                    title=f'Confirmation needed: {original_item.name} assignment',
                    message=f'Please confirm the assignment of {original_item.name}.',
                    notification_type='assign_item',
                    related_object_id=confirmation.id  # Assuming Notification model has a related_object_id field
                )

        messages.success(request, 'Assignment confirmation requests sent successfully!')
        return redirect('item_list')
    else:
        items = models.Item.objects.filter(assignedOffice__iexact=user_groups[0])

        # items = models.Item.objects.filter(assignedOffice__iexact=user_groups[0], status='confirmed')
        excluded_groups = list(user_groups)
        groups = Group.objects.exclude(name__in=excluded_groups)

        return render(request, 'inventory/assign_item.html', {'items': items, 'groups': groups, 'available_subgroups': available_subgroups})




@login_required
def confirm_assignment(request, confirmation_id):
    confirmation = get_object_or_404(models.AssignConfirmation, id=confirmation_id, assigned_to__users=request.user)
    user_subgroup = models.SubGroup.objects.filter(users=request.user).first()
    print("***********user_subgroup",user_subgroup )

    parent_group = user_subgroup.parent_group
    print("***********parent_group",parent_group )
    if request.method == 'POST':
        confirmed = request.POST.get('confirm', 'no') == 'yes'
        
        if confirmed:
            confirmation.confirmed = True
            confirmation.confirmation_date = timezone.now()
            confirmation.save()

            original_item = confirmation.item
            assigned_office = confirmation.assigned_to.name
            assigned_quantity = confirmation.quantity
            assignedBy = parent_group

            print(f"Original Item: {original_item.name}, Quantity: {original_item.quantity}")
            print(f"Assigned Office: {assigned_office}, Assigned Quantity: {assigned_quantity}")

            if original_item.consumable == 'Non-Consumable':
                # Transfer the entire item to the new office
                original_item.assignedOffice = assigned_office
                original_item.quantity = assigned_quantity
                original_item.assignedBy = parent_group

                original_item.assignedDateByGroup = timezone.now()
                original_item.save()
                print(f"Non-Consumable Item assigned to {assigned_office}")
            else:
                # Handle consumable items logic
                if original_item.quantity >= assigned_quantity:
                    new_store_quantity = original_item.quantity - assigned_quantity

                    # Update quantity for the original office
                    original_item.quantity = new_store_quantity
                    original_item.save()
                    print(f"Consumable Item new store quantity: {new_store_quantity}")

                    # Create a new item for the destination office
                    assigned_item = models.Item.objects.create(
                        name=original_item.name,
                        jinsi_no=original_item.jinsi_no,  # Transfer the jinsi_no
                        description=original_item.description,
                        consumable=original_item.consumable,
                        quantity=assigned_quantity,
                        unit=original_item.unit,
                        condition=original_item.condition,
                        category=original_item.category,
                        assignedOffice=assigned_office,
                        assignedBy = parent_group,

                        storeDate=original_item.storeDate,
                        assignedDateByGroup=timezone.now()
                    )
                    print(f"Created new item assigned to {assigned_office} with quantity {assigned_quantity}")
                else:
                    print("Error: Assigned quantity exceeds available quantity.")
                    messages.error(request, 'Assigned quantity exceeds available quantity.')

            messages.success(request, 'Item assignment confirmed successfully!')
        else:
            messages.info(request, 'Item assignment not confirmed.')

        return redirect('view_notifications')

    return render(request, 'inventory/notifications/confirm_assignment.html', {'confirmation': confirmation})


# @login_required
# def view_notifications(request, notification_type=None):
    
#     if notification_type:
#         notifications = models.Notification.objects.filter(user=request.user, notification_type=notification_type).order_by('-timestamp')
#     else:
#         notifications = models.Notification.objects.filter(user=request.user).order_by('-timestamp')
#     unread_notification_count = notifications.filter(is_read=False).count()

#     # Separate handling for request_item notifications
#     # if notification_type == 'request_item':
#     #     notifications = notifications.filter(notification_type='request_item')
#     #     return render(request, 'inventory/notifications/requestitemnot.html', {'notifications': notifications, 'unread_notification_count': unread_notification_count})




#     return render(request, 'inventory/notifications/view_notifications.html', {'notifications': notifications, 'unread_notification_count': unread_notification_count})

@login_required
def view_notifications(request, notification_type=None):
    if notification_type:
        # Split the notification types by comma and create a list
        notification_type_list = notification_type.split(',')
        # Filter notifications for the specified types
        notifications = models.Notification.objects.filter(user=request.user, notification_type__in=notification_type_list).order_by('-timestamp')
    else:
        # Retrieve all notifications if no specific types are provided
        notifications = models.Notification.objects.filter(user=request.user).order_by('-timestamp')
    
    # Count unread notifications
    unread_notification_count = notifications.filter(is_read=False).count()

    return render(request, 'inventory/notifications/view_notifications.html', {'notifications': notifications, 'unread_notification_count': unread_notification_count})


@login_required
def mark_notifications_as_read(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(models.Notification, id=notification_id, user=request.user)

        if not notification.is_read:
            notification.is_read = True
            notification.save()

            return JsonResponse({'success': True})

    return JsonResponse({'success': False})

@login_required

def notification_detail(request, notification_id):
    notification = get_object_or_404(models.Notification, id=notification_id, user=request.user)

    return render(request, 'inventory/notifications/notification_detail.html', {'notification': notification})

from .models import Item
from .forms import ReturnItemForm, ChangeStatusForm

@login_required

def return_item_list(request):
    user_subgroup = models.SubGroup.objects.filter(users=request.user).first()

    user_group = request.user.groups.values_list('name', flat=True).first()

    if user_subgroup:
        assigned_items = Item.objects.filter(assignedOffice=user_subgroup, consumable='Non-Consumable')
        return render(request, 'inventory/return_item_list.html', {'assigned_items': assigned_items})
    elif user_group:
        assigned_items = Item.objects.filter(assignedOffice=user_group, consumable='Non-Consumable')
        return render(request, 'inventory/return_item_list.html', {'assigned_items': assigned_items})

    else:
        messages.error(request, 'User group not found.')
        return redirect('item_list')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import ReturnItemForm

@login_required

def return_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id, consumable='Non-Consumable')

    if request.method == 'POST':

        form = ReturnItemForm(request.POST, request.FILES)
        user_subgroup = models.SubGroup.objects.filter(users=request.user).first()
        user_group = request.user.groups.values_list('name', flat=True).first()


        if form.is_valid():
            old_condition = item.condition
            item.condition = form.cleaned_data['condition']
            if item.condition == 'damaged':
                item.damagedDate = timezone.now()
            elif item.condition == 'maintained':
                item.maintainedDate = timezone.now()
            item.returnDate = timezone.now()

            if user_subgroup:
                parent_group = user_subgroup.parent_group
                item.assignedOffice = parent_group.name
            else:
                item.assignedOffice = 'FSCMO'

            print("Return Date:", item.returnDate)

        

            # Handle the uploaded file
            if 'returnitem_photo' in request.FILES:
                item.returnitem_photo = request.FILES['returnitem_photo']

            item.save()

            notify_user_group(request, item, operation='return_item')
            messages.success(request, 'Item returned successfully.')
            return redirect('item_list')
        else:
            print(form.errors)
    else:
        initial_data = {'condition': item.condition}

        form = ReturnItemForm(initial=initial_data)

    return render(request, 'inventory/return_item.html', {'form': form, 'item': item})

@login_required

def change_status(request, item_id):
    item = get_object_or_404(Item, pk=item_id, consumable='Non-Consumable')
    user_group = request.user.groups.first().name

    if request.method == 'POST':
        form = ChangeStatusForm(request.POST, request.FILES)

        if form.is_valid():
            old_condition = item.condition
            old_remarks = item.remarks

            item.condition = form.cleaned_data['condition']
            item.remarks = form.cleaned_data['remarks']
            if item.condition == 'damaged':
                item.damagedDate = timezone.now()
            elif item.condition == 'maintained':
                item.maintainedDate = timezone.now()
            item.changestatus_photo = form.cleaned_data['changestatus_photo']

            item.save()
            notify_user_group(request, item, operation='change_status', old_condition=old_condition, old_remarks=old_remarks)

            messages.success(request, 'Status changed successfully.')
            return redirect('item_list')
    else:
        # Set the initial value for the condition field to the current condition of the item
        initial_data = {'condition': item.condition}
        form = ChangeStatusForm(initial=initial_data)
        # form = ChangeStatusForm()

    return render(request, 'inventory/change_status.html', {'form': form, 'item': item})


def get_item_details(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    # Construct JSON response with item details
    item_details = {
        'store_date': item.storeDate,
        'storeassigned_date': item.assignedDateByStore,
        'groupassigned_date': item.assignedDateByGroup,

        'return_date': item.returnDate,
        'damaged_date': item.damagedDate,
        'maintained_date': item.maintainedDate,
    }
    return JsonResponse(item_details)

def notify_user_group(request, item, operation, old_condition=None, old_remarks=None):
    user_subgroup = models.SubGroup.objects.filter(users=request.user).first()

    # Check if the user belongs to a subgroup
    if user_subgroup:
        parent_group = user_subgroup.parent_group
        users_in_parent_group = User.objects.filter(groups=parent_group)

        # Create a notification for each user in the parent group
        for user_in_parent_group in users_in_parent_group:
            if operation == 'change_status':
                title = f'Status of "{item.name}" has been changed'
                message = f'The status of the item "{item.name}" has been changed from "{old_condition}" to "{item.condition}". Remarks: {old_remarks} -> {item.remarks}'
                notification_type = 'change_status'
            elif operation == 'return_item':
                title = f'The "{item.name}" has been returned'
                message = f'Item "{item.name}" has been returned to the {parent_group} group.'
                notification_type = 'return_item'

            elif operation == 'request_item':
                if request.user == user_in_parent_group:
                    title = f'Your request has been submitted to {parent_group}'
                    message = f'You have requested the item {item.name} (Quantity: {item.quantity} {item.unit}).'
                else:
                    title = f'New Item Request'
                    message = f'User {request.user.first_name} has requested the item {item.name} (Quantity: {item.quantity} {item.unit}).'
                notification_type = 'request_item'
                
            else:
                message = 'Invalid operation'

            models.Notification.objects.create(
                user=user_in_parent_group,
                title=title,
                message=message,
                notification_type=notification_type
            )
    else:
        # Handle the case when the user does not belong to any subgroup
        None



# @login_required
# def request_item(request):
#     if request.method == 'POST':
#         # Process form submission
#         selected_items = request.POST.getlist('selected_items')
#         requested_quantity_str = request.POST.get('requested_quantity', '0')

#         # Check if requested_quantity is a valid integer
#         try:
#             requested_quantity = int(requested_quantity_str)
#         except ValueError:
#             requested_quantity = 0
#     else:
#         # Render the initial page
#         items = models.Item.objects.filter(assignedOffice__iexact='Store')
#         groups = Group.objects.exclude(name__in=['SUPERADMIN', 'STORE'])
#         return render(request, 'inventory/request_item.html', {'items': items, 'groups': groups})

# def request_item(request):
#     if request.method == 'POST':
#         form = forms.ItemRequestForm(request.POST)
#         if form.is_valid():
#             item_name = form.cleaned_data['item']
#             item_count = form.cleaned_data['item_count']
#             current_datetime = datetime.now()

            
#             # Create a new ItemCount instance
#             item_count_instance = models.RequestItemCount.objects.create(date=current_datetime, item=item_name, item_count=item_count)

#             # Get the user's subgroup
#             user_subgroup = models.SubGroup.objects.filter(users=request.user).first()
#             if user_subgroup:
#                 # Associate the new ItemCount instance with the user's subgroup
#                 user_subgroup.requested_items.add(item_count_instance)
#                 user_subgroup.save()

#                 # Notify the parent group about the item request
#                 notify_user_group(request, item_name, 'request_item')

#                 # Redirect to a success page or do further processing
#                 return redirect('item_list')
#     else:
#         form = forms.ItemRequestForm()
    
#     return render(request, 'inventory/request_item.html', {'form': form})


# views.py



# def request_item(request):
#     if request.method == 'POST':
#         form = forms.ItemRequestForm(request.POST, request.FILES)
#         if form.is_valid():
#             item_name = form.cleaned_data['name']
#             # requestitem_photo = form.cleaned_data['requestitem_photo']
#             quantity = form.cleaned_data['quantity']
#             unit = form.cleaned_data['unit']
            
#             # Create a new RequestItemCount instance
#             item = models.RequestItemCount.objects.create(
#                 name=item_name,
#                 # requestitem_photo=requestitem_photo,
#                 quantity=quantity,
#                 unit=unit
#             )
#             # Get the user's subgroup
#             user_subgroup = models.SubGroup.objects.filter(users=request.user).first()
#             if user_subgroup:
#                 # Associate the new ItemCount instance with the user's subgroup
#                 user_subgroup.requested_items.add(item)
#                 user_subgroup.save()

#                 # Notify the parent group about the item request
#                 notify_user_group(request, item, 'request_item')

#             # Redirect to a success page or do further processing
#             return redirect('item_list')
#     else:
#         form = forms.ItemRequestForm()
    
#     return render(request, 'inventory/request_item.html', {'form': form})


# @login_required
# def request_item(request):
#     if request.method == 'POST':
#         form = forms.ItemRequestForm(request.POST, request.FILES)
#         if form.is_valid():
#             item_name = form.cleaned_data['name']
#             quantity = form.cleaned_data['quantity']
#             unit = form.cleaned_data['unit']
            
#             # Create a new RequestItemCount instance
#             item = models.RequestItemCount.objects.create(
#                 name=item_name,
#                 quantity=quantity,
#                 unit=unit
#             )

#             # Get the user's subgroup
#             user_subgroup = models.SubGroup.objects.filter(users=request.user).first()
#             if user_subgroup:
#                 # Associate the new ItemCount instance with the user's subgroup
#                 user_subgroup.requested_items.add(item)
#                 user_subgroup.save()

#                 # Notify the parent group about the item request
#                 notify_user_group(request, item, 'request_item')

#             # Redirect to a success page or do further processing
#             return redirect('item_list')
#     else:
#         form = forms.ItemRequestForm()
    
#     return render(request, 'inventory/request_item.html', {'form': form})

from django.shortcuts import render, redirect
from . import forms, models
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# @login_required
# def request_item(request):
#     if request.method == 'POST':
#         form = forms.ItemRequestForm(request.POST, request.FILES)
#         if form.is_valid():
#             item_name = form.cleaned_data['name']
#             quantity = form.cleaned_data['quantity']
#             unit = form.cleaned_data['unit']
#             description = form.cleaned_data['description']
#             requestitem_photo = form.cleaned_data['requestitem_photo']

#             # Create a new RequestItemCount instance
#             item = models.RequestItemCount.objects.create(
#                 name=item_name,
#                 quantity=quantity,
#                 unit=unit,
#                 requested_by=request.user,  # Assign the requesting user
#                 description=description,
#                 requestitem_photo=requestitem_photo
#             )

#             # Get the user's subgroup
#             user_subgroup = models.SubGroup.objects.filter(users=request.user).first()
#             if user_subgroup:
#                 # Associate the new ItemCount instance with the user's subgroup
#                 user_subgroup.requested_items.add(item)
#                 user_subgroup.save()

#                 # Notify the parent group about the item request
#                 notify_user_group(request, item, 'request_item')

#             # Redirect to a success page or do further processing
#             return redirect('item_list')
#     else:
#         form = forms.ItemRequestForm()
    
#     return render(request, 'inventory/request_item.html', {'form': form})


# from .models import RequestItemCount

@login_required
def request_item_list(request):
    # Get the user's groups and subgroups
    user_groups = request.user.groups.values_list('name', flat=True)

    # Initialize assigned_offices list
    assigned_offices = []

    if 'SUPERADMIN' in user_groups or 'FSCMO' in user_groups:
        # Fetch all request items
        all_request_items = RequestItemCount.objects.all()

    else:
        # Retrieve the user's group
        user_group = user_groups.first()

        # Check if the user belongs to any subgroup
        subgroup = models.SubGroup.objects.filter(users=request.user).first()

        if subgroup:
            # If user is from a subgroup, display items requested by that subgroup only
            all_request_items = subgroup.requested_items.all()
        else:
            # If user is from another group, display items requested by related subgroups
            related_subgroups = models.GroupSubgroupMapping.objects.filter(group__name=user_group).values_list('subgroup__name', flat=True)
            all_request_items = RequestItemCount.objects.filter(subgroups__name__in=related_subgroups)

    return render(request, 'inventory/request_item_list.html', {'all_request_items': all_request_items})






#####Request item code


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from .models import ItemRequest, SubGroup
from .forms import ItemRequestForm

@login_required
def request_item(request):
    user_groups = request.user.groups.values_list('name', flat=True)
    user_subgroup = SubGroup.objects.filter(users=request.user).first()
  

    if request.method == 'POST':
        form = ItemRequestForm(request.POST, request.FILES)

        # form = ItemRequestForm(request.POST)
        if form.is_valid():
            item_request = form.save(commit=False)
            if user_subgroup:
                item_request.requested_subgroup = user_subgroup
                item_request.requested_group = user_subgroup.parent_group
                item_request.status = {
                    "subgroup": "requested",
                    "group": "",
                    "officer": "",
                    "under_secretary": "",
                    "joint_secretary": ""
                }
                item_request.dates = {
                    "subgroup": timezone.now().strftime('%Y-%m-%d'),
                    "group": "",
                    "officer": "",
                    "under_secretary": "",
                    "joint_secretary": ""
                }
            elif user_groups :
                item_request.requested_group = user_groups[0]
                item_request.status = {
                    "subgroup": "",
                    "group": "requested",
                    "officer": "",
                    "under_secretary": "",
                    "joint_secretary": ""
                }
                item_request.dates = {
                    "subgroup": "",
                    "group": timezone.now().strftime('%Y-%m-%d'),
                    "officer": "",
                    "under_secretary": "",
                    "joint_secretary": ""
                }
            item_request.requestitem_photo = form.cleaned_data['requestitem_photo']
    

            item_request.save()
            return redirect('home')
    else:
        form = ItemRequestForm()

    return render(request, 'inventory/request_item_new.html', {'form': form,  'user_subgroup': user_subgroup,
})

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import ItemRequest, SubGroup
from .forms import ItemRequestForm


from django.http import HttpResponseServerError

from django.http import HttpResponseServerError

@login_required
def process_request(request, item_request_id):
    try:
        item_request = get_object_or_404(ItemRequest, id=item_request_id)

        # user_groups = request.user.groups.values_list('name', flat=True)

        user_groups = request.user.groups.values_list('name', flat=True)
        user_subgroup = SubGroup.objects.filter(users=request.user).first()



        role = None
        parent_group = None

        if user_groups[0] == str(item_request.requested_group):
            role = 'group'
        elif 'OFFICER' in user_groups:
            role = 'officer'
        elif 'UNDERSECRETARY' in user_groups:
            role = 'under_secretary'
        elif 'JOINTSECRETARY' in user_groups:
            role = 'joint_secretary'
        elif user_subgroup == item_request.requested_subgroup:
            role = 'subgroup'
        else:
            None

        if request.method == 'POST':
            form = ItemRequestForm(request.POST, instance=item_request, role=role)
            action = request.POST.get('action')


            if form.is_valid():
                item_request = form.save(commit=False)

                if role == 'group':
                    if action =='edit':
                        item_request.status['group'] = 'edited_forwarded'
                    elif action =='reject':
                        item_request.status['group'] = 'rejected'
                    else:
                        item_request.status['group'] = 'forwarded'
                        item_request.item_quantity['group'] =  item_request.item_quantity['subgroup']                  
                    item_request.dates['group'] = timezone.now().strftime('%Y-%m-%d')
                elif role == 'officer':
                    if action =='edit':
                        item_request.status['officer'] = 'edited_forwarded'

                    elif action =='reject':
                        item_request.status['officer'] = 'rejected'

                    else:
                        item_request.status['officer'] = 'forwarded'

                        item_request.item_quantity['officer'] =  item_request.item_quantity['group']  
                    item_request.available = form.cleaned_data['available']
                    item_request.available_description = form.cleaned_data['available_description'] 
                    print("Officer Values - Available:", item_request.available)
                    print("Officer Values - Available Description:", item_request.available_description)

                    item_request.save()


                    item_request.dates['officer'] = timezone.now().strftime('%Y-%m-%d')
                elif role == 'under_secretary':
                    if action =='edit':
                        item_request.status['under_secretary'] = 'edited_forwarded'
                        print("@@@Role -under_secretary , edited_forwarded")

                    elif action =='reject':
                        item_request.status['under_secretary'] = 'rejected'
                        print("@@@Role -under_secretary , rejected")

                    else:
                        item_request.status['under_secretary'] = 'forwarded'
                        print("@@@Role -under_secretary , forwarded")

                        item_request.item_quantity['under_secretary'] =  item_request.item_quantity['officer']   
                    # item_request.available = item_request.available  # Keep the value from the officer
                    # item_request.available_description = item_request.available_description  # Keep the value from the office  
                    print(" under_secretary Values - Available:", item_request.available)
                    print("under_secretary Values - Available Description:", item_request.available_description)                    
                    item_request.dates['under_secretary'] = timezone.now().strftime('%Y-%m-%d')

                elif role == 'joint_secretary':
                    if action =='edit_accept':
                        item_request.status['joint_secretary'] = 'edited_accepted'
                        print("@@@Role -joint_secretary , edited_accepted")

                    elif action =='reject':
                        item_request.status['joint_secretary'] = 'rejected'
                        print("@@@Role -joint_secretary , rejected")

                    else:
                        item_request.status['joint_secretary'] = 'accepted'
                        print("@@@Role -joint_secretary , accepted")

                        item_request.item_quantity['joint_secretary'] =  item_request.item_quantity['under_secretary']  
                    # item_request.available = item_request.available  # Keep the value from the under_secretary
                    # item_request.available_description = item_request.available_description  # Keep the value from the under_secretary              

                    item_request.dates['joint_secretary'] = timezone.now().strftime('%Y-%m-%d')
                item_request.available = item_request.available  
                item_request.available_description = item_request.available_description  
                item_request.unit=item_request.unit

                item_request.save()
                return redirect('item_request_list')
            else:
                # Print form errors to terminal
                print(form.errors)
        else:
            form = ItemRequestForm(instance=item_request, role=role)

        return render(request, 'inventory/process_request.html', {'form': form, 'role': role, 'item_request': item_request})

    except Exception as e:
        # Log the exception
        print(f"An error occurred: {str(e)}")
        return HttpResponseServerError("An error occurred while processing the request. Please try again later.")


@login_required
def item_request_list(request):
    user_groups = request.user.groups.values_list('name', flat=True)
    user_group = user_groups[0]
    if 'FSCMO' in user_groups:
            item_requests = ItemRequest.objects.filter(status__joint_secretary__in = ['accepted'])
    else:
        item_requests = ItemRequest.objects.none()
        # user_subgroup = SubGroup.objects.filter(users=request.user).first()
        if 'OFFICER' in user_groups:
            item_requests = ItemRequest.objects.filter(status__group__in = ['requested', 'forwarded', 'edited_forwarded'] , status__officer='')
        elif 'UNDERSECRETARY' in user_groups:
            item_requests = ItemRequest.objects.filter(status__officer__in = ['requested', 'forwarded', 'edited_forwarded'] , status__under_secretary='')
        elif 'JOINTSECRETARY' in user_groups:
            item_requests = ItemRequest.objects.filter(status__under_secretary__in = ['requested', 'forwarded', 'edited_forwarded'] , status__joint_secretary='')
        else :
            # item_requests = ItemRequest.objects.filter(
            #     requested_group__in=user_groups,
            #     Q(status__group__isnull=False) & Q(status__group__ne='')
            # )
            item_requests = ItemRequest.objects.filter(requested_group__in=user_groups, status__subgroup ='requested', status__group='')

            # item_requests = ItemRequest.objects.filter(Q(requested_group__in=user_groups) & Q(status__group__isnull=False) & Q(status__group__ne='') )
    print("item_requests", item_requests, user_groups , "user_groups")
    return render(request, 'inventory/item_request_list.html', {'item_requests': item_requests,'user_group': user_group })



@login_required
def item_request_list_sent(request):
    user_groups = request.user.groups.values_list('name', flat=True)
    subgroup = models.SubGroup.objects.filter(users=request.user)
    print(subgroup, "^^^^^^^^^requested_group__in")
    user_group = user_groups[0]
    if 'FSCMO' in user_groups:
            item_requests = ItemRequest.objects.all
    else:
        item_requests = ItemRequest.objects.none()
        # user_subgroup = SubGroup.objects.filter(users=request.user).first()
        if 'OFFICER' in user_groups:
            item_requests = ItemRequest.objects.filter(status__officer__in = ['forwarded', 'edited_forwarded', 'rejected'] )
        elif 'UNDERSECRETARY' in user_groups:
            item_requests = ItemRequest.objects.filter(status__under_secretary__in = [ 'forwarded', 'edited_forwarded', 'rejected'] )
        elif 'JOINTSECRETARY' in user_groups:
            item_requests = ItemRequest.objects.filter(status__joint_secretary__in = ['rejected', 'accepted', 'edited_accepted'] )
        elif subgroup :
            # item_requests = ItemRequest.objects.filter(
            #     requested_group__in=user_groups,
            #     Q(status__group__isnull=False) & Q(status__group__ne='')
            # )
            item_requests = ItemRequest.objects.filter( requested_subgroup = subgroup[0], status__subgroup__in =['requested'])
        else  :
            # item_requests = ItemRequest.objects.filter(
            #     requested_group__in=user_groups,
            #     Q(status__group__isnull=False) & Q(status__group__ne='')
            # )
            item_requests = ItemRequest.objects.filter(requested_group__in=user_groups, status__group__in=['requested', 'forwarded', 'edited_forwarded'])

            # item_requests = ItemRequest.objects.filter(Q(requested_group__in=user_groups) & Q(status__group__isnull=False) & Q(status__group__ne='') )
    print("item_requests", item_requests, user_groups , "user_groups")
    return render(request, 'inventory/item_request_list_sent.html', {'item_requests': item_requests,'user_group': user_group })