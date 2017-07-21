from django import forms

p1 = [25, 50, 100, 200, 500, 1000]
pagination = zip(p1, p1)

class MovieFilterForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100, required=False, widget=forms.TextInput(attrs={'type':'search', 'form':'movieform'}))
    notags = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'form':'movieform', 'class':'tagcheck'}))
    perpage = forms.ChoiceField(choices= pagination, initial=100, widget=forms.Select(attrs={'form':'movieform'}))