from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from . import views
urlpatterns=[
	
	path('',views.home,name='home'),
	##INVENTORY SYSTEM
    path('assign_item/', views.assign_item, name='assign_item'),
    path('add_item/', views.add_item, name='add_item'),
    path('bulk_add_items/', views.bulk_add_items, name='bulk_add_items'),

    path('item_list/', views.item_list, name='item_list'),
    path('delete_item/<int:item_id>/', views.delete_item, name='delete_item'),

    path('assign_item_by_store/', views.assign_item_by_store, name='assign_item_by_store'),


	# path('request_item/', views.request_item, name='request_item'),
    path('request_item_list/', views.request_item_list, name='request_item_list'),

	path('return_item_list/', views.return_item_list, name='return_item_list'),
	path('return_item/<int:item_id>/', views.return_item, name='return_item'),
	path('change_status/<int:item_id>/', views.change_status, name='change_status'),
    # path('export_to_excel/', views.export_to_excel, name='export_to_excel'),
	path('filter_items/', views.filter_items, name='filter_items'),
    path('export_filtered_to_excel/', views.export_filtered_to_excel, name='export_filtered_to_excel'),
	path('update-profile',views.update_profile,name='update_profile'),
	path('view_notifications/', views.view_notifications, name='view_notifications'),
	path('view_notifications/<str:notification_type>/', views.view_notifications, name='view_notifications'),
	path('mark_notifications_as_read/<int:notification_id>/', views.mark_notifications_as_read, name='mark_notifications_as_read'),
    path('edit-form/<int:item_id>/', views.edit_item, name='edit_item'),
	path('contact',views.contact_page,name='contact_page'),
	path('accounts/signup',views.signup,name='signup'),
	path('accounts/login',views.login,name='login'),
	path('notification_detail/<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('get_item_details/<int:item_id>/', views.get_item_details, name='get_item_details'),
    path('confirm-assignment/<int:confirmation_id>/', views.confirm_assignment, name='confirm_assignment'),
    path('confirm_assignment_for_store/<int:confirmation_id>/', views.confirm_assignment_for_store, name='confirm_assignment_for_store'),


    # path('confirm_item/<int:pending_item_id>/', views.confirm_item, name='confirm_item'),
    path('pending_items/', views.pending_items_list, name='pending_items_list'),

    # path('item_log/<int:item_id>/', views.item_log, name='item_log'),

    path('reset_user_password/', views.reset_user_password, name='reset_user_password'),
    path('get_user_data/<int:user_id>/', views.get_user_data, name='get_user_data'),
    path('cancel_update/', views.cancel_update, name='cancel_update'),
    path('update_user_profile/', views.update_user_profile, name='update_user_profile'),
    path('user_list/', views.user_list, name='user_list'),
    path('user/<int:user_id>/delete/', views.delete_user, name='delete_user'),


#Groups
    path('add_group/', views.add_group, name='add_group'),
	path('group_list/', views.group_list, name='group_list'),
    path('group/<int:group_id>/delete/', views.delete_group, name='delete_group'),

    path('add_subgroup/', views.add_subgroup, name='add_subgroup'),
	path('fetch_subgroups/', views.fetch_subgroups, name='fetch_subgroups'),
    path('subgroups/', views.subgroup_list, name='subgroup_list'),
    path('subgroup/<int:subgroup_id>/delete/', views.delete_subgroup, name='delete_subgroup'),


    path('photo_list/<int:item_pk>/', views.photo_list, name='photo_list'),

    # path('view_requests/', views.view_requests, name='view_requests'),

    path('request/', views.request_item, name='request_item'),
    path('process/<int:item_request_id>/', views.process_request, name='process_request'),
    path('requests/', views.item_request_list, name='item_request_list'),
    path('requests_sent/', views.item_request_list_sent, name='item_request_list_sent'),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)