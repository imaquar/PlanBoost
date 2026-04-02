from django import forms


class NoteForm(forms.Form):
    label = forms.CharField(max_length=50, label='Title')
    text = forms.CharField(widget=forms.Textarea, label='Note', required=False)