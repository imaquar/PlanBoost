from django.shortcuts import render
from notes.models import Note
from .forms import NoteForm
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    form = NoteForm()
    note = Note.objects.filter(user=request.user)
    return render(request, 'notes/notes.html', {'form' : form, 'note' : note})

@login_required
def note(request, id):
    try:
        note = Note.objects.get(id=id, user=request.user)
    except Note.DoesNotExist:
        return HttpResponseNotFound('<h2>Note not found</h2>')
    return render(request, 'notes/note.html', {'note' : note})
