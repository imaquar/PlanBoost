from django import forms


class NoteForm(forms.Form):
    label = forms.CharField(max_length=50, label='Title', widget=forms.TextInput(attrs={'placeholder': 'title'}),)
    text = forms.CharField(required=False, label='Note', widget=forms.Textarea(attrs={'placeholder': 'note'}),)