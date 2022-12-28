from django import forms
from .models import Restaurant
from accounts.validators import allow_only_images_validator


class RestaurantForm(forms.ModelForm):
    restaurant_license=forms.FileField(widget=forms.FileInput(attrs={'class':'btn btn-info'}),validators=[allow_only_images_validator])
    
    # restaurant_license = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}))#, validators=[allow_only_images_validator])
    class Meta:
        model = Restaurant
        fields = ['restaurant_name', 'restaurant_license']


# class OpeningHourForm(forms.ModelForm):
#     class Meta:
#         model = OpeningHour
#         fields = ['day', 'from_hour', 'to_hour', 'is_closed']