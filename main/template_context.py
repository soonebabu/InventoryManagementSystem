from . import models

def get_logo(request):
	logo=models.AppSetting.objects.first()
	data={}
	if logo is not None:
		data['logo'] = logo.image_tag
	else:
		data['logo'] = "Home" # or any other suitable value, such as an empty string	
	return data