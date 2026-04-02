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

@login_required
def create(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = Note()
            note.label = form.cleaned_data['label']
            note.text = form.cleaned_data['text']
            note.user = request.user
            note.save()
            return HttpResponseRedirect('/notes/')
    else:
        form = NoteForm()

    return render(request, 'notes/create.html', {'form': form})


@login_required
def edit(request, id):
    try:
        note = Note.objects.get(id=id, user=request.user)
    except Note.DoesNotExist:
        return HttpResponseNotFound('<h2>Note not found</h2>')

    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note.label = form.cleaned_data['label']
            note.text = form.cleaned_data['text']
            note.save()
        return HttpResponseRedirect(f'/notes/note/{id}/')
    else:
        form = NoteForm(model_to_dict(note))
        return render(request, 'notes/edit.html', {'form': form})
