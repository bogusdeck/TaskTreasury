from django import forms
from PIL import Image
from Authentication.models import Task

class AdminTaskForm(forms.ModelForm):
    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            img = Image.open(logo)
            width ,height = img.size
            if width != height:
                raise forms.ValidationError("Logo must be square in shape")
        return logo
    class Meta:
        model = Task
        fields = ["name", "link", "category", "subcategory", "points", "logo"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "link": forms.URLInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "subcategory": forms.Select(attrs={"class": "form-control"}),
            "points": forms.NumberInput(attrs={"class": "form-control"}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
