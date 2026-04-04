from django import forms


class TaskForm(forms.Form):
    label = forms.CharField(max_length=50, label='Title')
    description = forms.CharField(widget=forms.Textarea, label='Description', required=False)
    deadline = forms.DateTimeField(label='Deadline')
    priority = forms.ChoiceField(choices=[(1, "Low"), (2, "Medium"), (3, "High")], label='Priority')
