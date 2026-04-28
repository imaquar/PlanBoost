from django.shortcuts import render
from notes.models import Note
from .forms import NoteForm
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from urllib.parse import urlencode, urlparse

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
    next_url = request.GET.get('next', '').strip()
    if not next_url:
        referer = request.META.get('HTTP_REFERER', '').strip()
        if referer:
            parsed = urlparse(referer)
            if parsed.path.startswith('/notes/'):
                next_url = parsed.path
                if parsed.query:
                    next_url += '?' + parsed.query
    if not next_url.startswith('/'):
        next_url = '/notes/'
    return render(request, 'notes/note.html', {'note': note, 'next': next_url})

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

    next_url = request.GET.get('next', '').strip() or request.POST.get('next', '').strip()
    if not next_url.startswith('/'):
        next_url = '/notes/'

    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note.label = form.cleaned_data['label']
            note.text = form.cleaned_data['text']
            note.save()
        note_url = reverse('notes:note', args=[id])
        if next_url and next_url != '/notes/':
            return HttpResponseRedirect(f'{note_url}?{urlencode({"next": next_url})}')
        return HttpResponseRedirect(note_url)
    else:
        form = NoteForm(model_to_dict(note))
        return render(request, 'notes/edit.html', {'form': form, 'note': note, 'next': next_url})

@login_required
@require_POST
def delete(request, id):
    try:
        note = Note.objects.get(id=id, user=request.user)
    except Note.DoesNotExist:
        return HttpResponseNotFound('<h2>Note not found</h2>')
    note.delete()
    next_url = request.POST.get('next', '').strip()
    if next_url.startswith('/'):
        return HttpResponseRedirect(next_url)
    return HttpResponseRedirect('/notes/')
