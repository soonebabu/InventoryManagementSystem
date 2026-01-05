from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.models import Group  
from . import models
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.contrib.auth.forms import AuthenticationForm
from nepali_datetime_field.forms import NepaliDateField
from django.contrib.auth import update_session_auth_hash


# USER CREATION
# class SignUp(UserCreationForm):
# 	class Meta:
# 		model=User
# 		fields=('first_name','last_name','email','username','password1','password2')

# 	group = forms.ModelChoiceField(
#         queryset=Group.objects.all(),
#         label='Select User Group'
#     )


class UploadFileForm(forms.Form):
    file = forms.FileField()


class SignUp(UserCreationForm):
    
    
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label='Select Group', required=False)
    subgroup = forms.ModelChoiceField(queryset=models.SubGroup.objects.all(), label='Select Subgroup', required=False)
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2', 'subgroup')







class LoginForm(AuthenticationForm):
    class Meta:
        model = User	

#Update Profile
# class ProfileForm(UserChangeForm):
# 	class Meta:
# 		model=User
# 		fields=('first_name','last_name','email','username')

class CustomProfileForm(UserChangeForm):
    password1 = forms.CharField(widget=forms.PasswordInput(), label='New Password', required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(), label='Confirm New Password', required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.request and self.request.user.is_authenticated:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
        else:
            self.fields['password1'].required = True
            self.fields['password2'].required = True

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data["password1"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if password1:
            user.set_password(password1)
        elif 'password1' in self.changed_data:
        # If password1 is empty but it's in changed_data, clear the password
            user.set_password(None)
        if commit:
            user.save()
            update_session_auth_hash(self.request, user)
        return user


class UserUpdateForm(UserChangeForm):
    user_to_update = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='Select User to Update',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['user_to_update'].label_from_instance = lambda obj: f"{obj.username} - {obj.get_full_name()}"

    def clean_user_to_update(self):
        user_to_update = self.cleaned_data.get('user_to_update')
        if user_to_update == self.instance:
            raise forms.ValidationError("Cannot update your own profile using this form.")
        return user_to_update

    def clean(self):
        cleaned_data = super().clean()

         # Check if at least one field (excluding username) is updated
        fields_to_check = [field for field in self.Meta.fields if field != 'username']
        if not any(cleaned_data.get(field) for field in fields_to_check):
            raise forms.ValidationError("At least one field (other than username) should be updated.")

        return cleaned_data

class ResetPasswordForm(forms.Form):
    user_to_reset = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='Select User to Reset Password',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def save(self, commit=True):
        user_to_reset = self.cleaned_data['user_to_reset']
        new_password = self.cleaned_data['new_password']
        
        # Set the new password
        user_to_reset.set_password(new_password)

        if commit:
            user_to_reset.save()
        
        return user_to_reset




#Add Group
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

#Add SubGroup
class SubGroupForm(forms.ModelForm):
    class Meta:
        model = models.SubGroup
        fields = ['name', 'parent_group']

    def clean_name(self):
        name = self.cleaned_data['name']
        parent_group = self.cleaned_data.get('parent_group')

        # Check if a subgroup with the same name exists under the same parent group
        if parent_group and models.SubGroup.objects.filter(name=name, parent_group=parent_group).exists():
            raise forms.ValidationError("A subgroup with this name already exists under the selected parent group.")

        return name




class ItemForm(forms.ModelForm):
    class Meta:
        model = models.Item
        fields = '__all__'
        exclude = ['status']  # Exclude the status field

        widgets = {
            'consumable': forms.RadioSelect(),
            
        }

    def clean(self):
        cleaned_data = super().clean()
        consumable = cleaned_data.get('consumable')
        jinsi_no = cleaned_data.get('jinsi_no')

        if consumable == 'Non-Consumable':
            # Check if jinsi_no is provided for non-consumable items
            if not jinsi_no:
                raise forms.ValidationError("Jinsi_no is required for non-consumable items.")
            else:
                # Check if jinsi_no is unique for non-consumable items
                if models.Item.objects.filter(consumable='Non-Consumable', jinsi_no=jinsi_no).exists():
                    raise forms.ValidationError("Jinsi_no must be unique for non-consumable items.")

        return cleaned_data

        

class ItemRequestForm(forms.ModelForm):
    class Meta:
        model = models.RequestItemCount
        fields = ['name', 'quantity', 'unit', 'requestitem_photo', 'description', 'status']

class ReturnItemForm(forms.ModelForm):
    # returnitem_photo = forms.ImageField()

    class Meta:
        model = models.Item

        fields = ['condition','remarks', 'returnitem_photo', 'returnDate']  # Add any fields needed for the return item form

    def __init__(self, *args, **kwargs):
        super(ReturnItemForm, self).__init__(*args, **kwargs)
        # Add the 'required' attribute to the remarks field
        self.fields['remarks'].required = True

class ChangeStatusForm(forms.ModelForm):
    class Meta:
        model = models.Item
        fields = ['condition', 'remarks', 'changestatus_photo']

    def __init__(self, *args, **kwargs):
        super(ChangeStatusForm, self).__init__(*args, **kwargs)
        # Add the 'required' attribute to the remarks field
        self.fields['remarks'].required = True

        self.initial_condition = self.instance.condition

    def clean_condition(self):
        cleaned_data = super().clean()

        new_condition = cleaned_data.get('condition')

        if self.initial_condition == 'new':
            # Initial condition is 'new', so allow changing to 'operational', 'damaged', or 'maintained'
            allowed_conditions = ['operational', 'damaged', 'maintained']
        elif self.initial_condition == 'operational':
            # Initial condition is 'operational', so allow changing to 'damaged' or 'maintained'
            allowed_conditions = ['damaged', 'maintained']
        elif self.initial_condition == 'damaged':
            # Initial condition is 'damaged', so allow changing to 'operational' or 'maintained'
            allowed_conditions = ['operational', 'maintained']
        elif self.initial_condition == 'maintained':
            # Initial condition is 'maintained', so allow changing to 'operational' or 'damaged'
            allowed_conditions = ['operational', 'damaged']
        else:
            # Unrecognized initial condition, allow all conditions
            allowed_conditions = ['new', 'operational', 'damaged', 'maintained']

        if new_condition not in allowed_conditions:
            self.add_error(None, forms.ValidationError(f"Invalid value for Condition change. Condition cannot be changed to {new_condition} "))

        return new_condition

class ExportForm(forms.Form):
    assigned_office = forms.CharField(required=False)
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
    consumable = forms.BooleanField(required=False)
    condition = forms.ChoiceField(choices=models.Item.CONDITION, required=False)


# from django import forms
# from .models import ItemRequest

# class ItemRequestForm(forms.ModelForm):
#     class Meta:
#         model = ItemRequest
#         fields = ['item_name', 'item_quantity']

#     def __init__(self, *args, **kwargs):
#         role = kwargs.pop('role', None)
#         super(ItemRequestForm, self).__init__(*args, **kwargs)
        
#         # Initialize common fields
#         self.fields['item_name'].widget.attrs.update()
        
#         # Update form fields based on role
#         if role == 'subgroup':
#             self.fields['item_quantity'].widget.attrs.update({'readonly': True})
#         elif role == 'group':
#             self.fields['item_quantity'] = forms.IntegerField()
#         elif role in ['officer', 'under_secretary', 'joint_secretary']:
#             self.fields['item_quantity'] = forms.IntegerField()
        
#         # Add status actions based on role
#         if role:
#             self.fields['status_action'] = forms.ChoiceField(
#                 choices=[
#                     ('forward', 'Forward'),
#                     ('edit', 'Edit and Forward'),
#                     ('reject', 'Reject')
#                 ],
#                 widget=forms.RadioSelect
#             )

#     def save(self, commit=True, role = None):
#         instance = super(ItemRequestForm, self).save(commit=False)
#         status_action = self.cleaned_data.get('status_action', None)
        
#         # Update status and dates based on action
#         if status_action == 'edit':
#             instance.status[role] = 'edited_forwarded'
#         elif status_action == 'reject':
#             instance.status[role] = 'rejected'
#         else:
#             instance.status[role] = 'forwarded'

#         if commit:
#             instance.save()
#         return instance


from django import forms
from .models import ItemRequest


class ItemRequestForm(forms.ModelForm):
    available_description = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ItemRequest
        fields = ['item_name','available','available_description', 'unit','requestitem_photo', 'description' ]
        widgets ={
            'available': forms.RadioSelect(attrs={'class': 'form-check-input'}),

        }

    subgroup_quantity = forms.IntegerField(label='Subgroup Quantity', required=False)
    group_quantity = forms.IntegerField(label='Group Quantity', required=False)
    officer_quantity = forms.IntegerField(label='Officer Quantity', required=False)
    under_secretary_quantity = forms.IntegerField(label='Under Secretary Quantity', required=False)
    joint_secretary_quantity = forms.IntegerField(label='Joint Secretary Quantity', required=False)

    def __init__(self, *args, **kwargs):
        role = kwargs.pop('role', None)
        super(ItemRequestForm, self).__init__(*args, **kwargs)
        
        if role:
            self.fields['status_action'] = forms.ChoiceField(
                choices=[
                    ('forward', 'Forward'),
                    ('edit', 'Edit and Forward'),
                    ('reject', 'Reject')
                ],
                widget=forms.RadioSelect,
                required=False
            )
        
        # Initialize item quantities from JSON field
        instance = kwargs.get('instance')
        if instance:
            item_quantity = instance.item_quantity
            self.fields['subgroup_quantity'].initial = item_quantity.get('subgroup', 0)
            self.fields['group_quantity'].initial = item_quantity.get('group', 0)
            self.fields['officer_quantity'].initial = item_quantity.get('officer', 0)
            self.fields['under_secretary_quantity'].initial = item_quantity.get('under_secretary', 0)
            self.fields['joint_secretary_quantity'].initial = item_quantity.get('joint_secretary', 0)

        if role in ['under_secretary', 'joint_secretary']:
            
            for field in ['available', 'available_description']:
                self.fields[field].widget.attrs['readonly'] = True
                self.fields[field].widget.attrs['disabled'] = True   
                self.fields[field].widget = forms.HiddenInput()  # Add hidden input to store values
 

        self.fields['available_description'].required = False  # Make description field optional

    
    
    def save(self, commit=True):
        instance = super(ItemRequestForm, self).save(commit=False)
        
        # Populate item_quantity JSON field
        instance.item_quantity = {
            'subgroup': self.cleaned_data.get('subgroup_quantity', 0),
            'group': self.cleaned_data.get('group_quantity', 0),
            'officer': self.cleaned_data.get('officer_quantity', 0),
            'under_secretary': self.cleaned_data.get('under_secretary_quantity', 0),
            'joint_secretary': self.cleaned_data.get('joint_secretary_quantity', 0),
        }
        
        # Handle status action and role updates
        status_action = self.cleaned_data.get('status_action', None)
        role = self.initial.get('role')
        if role and status_action:
            if status_action == 'edit':
                instance.status[role] = 'edited_forwarded'
            elif status_action == 'reject':
                instance.status[role] = 'rejected'
            else:
                instance.status[role] = 'forwarded'

        if role == 'officer':
            instance.available = self.cleaned_data['available']
            instance.available_description = self.cleaned_data['available_description']

        else:
            # Ensure the fields are retained when the form is submitted
            instance.available = self.initial.get('available', instance.available)
            instance.available_description = self.initial.get('available_description', instance.available_description)
        instance.unit = self.initial.get('unit', instance.unit)


        if commit:
            instance.save()
        return instance
