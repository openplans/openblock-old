from django import forms


class NewsItemForm(forms.Form):

    def clean(self):
        data = self.cleaned_data
        
        lat = data.get("latitude", None)
        lon = data.get("longitude", None)
        
        if lat is None and lon is None: 
            raise forms.ValidationError("Please specify a location on the map.")

        return data

class NeighborMessageForm(NewsItemForm): 
    title = forms.CharField(max_length=255, label="Title")
    location_name = forms.CharField(max_length=255, label="Address or Location", required=False)
    url = forms.CharField(max_length=2048, label="Link to more information", required=False)
    image_url = forms.CharField(max_length=2048, label="Link to image", required=False)
    categories = forms.CharField(max_length=10240, required=False, help_text="Separate with commas")
    description = forms.CharField(max_length=10240, label="Message", widget=forms.Textarea)
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput)

    
class NeighborEventForm(NewsItemForm): 
    title = forms.CharField(max_length=255, label="Title")
    location_name = forms.CharField(max_length=255, label="Address or Location", required=False)
    item_date = forms.DateField(label="Date")
    start_time = forms.TimeField(label="Start Time", required=False, input_formats=("%I:%M%p",))
    end_time = forms.TimeField(label="End Time", required=False, input_formats=("%I:%M%p",))
    url = forms.CharField(max_length=2048, label="Link to more information", required=False)
    image_url = forms.CharField(max_length=2048, label="Link to image", required=False)
    categories = forms.CharField(max_length=10240, required=False, help_text="Separate with commas")
    description = forms.CharField(max_length=10240, label="Message", widget=forms.Textarea)
    latitude = forms.FloatField(required=False, widget=forms.HiddenInput)
    longitude = forms.FloatField(required=False, widget=forms.HiddenInput)
