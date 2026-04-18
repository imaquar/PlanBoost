from django import forms


class TaskForm(forms.Form):
    label = forms.CharField(max_length=50, label='Title', widget=forms.TextInput(attrs={'placeholder': 'title'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'description'}), label='Description', required=False)
    deadline = forms.DateTimeField(
        label='Deadline',
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    priority = forms.ChoiceField(choices=[(1, "Low"), (2, "Medium"), (3, "High")], label='Priority')
