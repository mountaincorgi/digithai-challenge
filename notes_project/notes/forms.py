from django import forms


class SearchForm(forms.Form):
    q = forms.CharField(max_length=140, required=False, label="Search")
