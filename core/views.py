from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Photo, Album
from .forms import PhotoForm, AlbumForm
from django.contrib.auth.decorators import login_required 
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.db.models import Count, Min, Q

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return redirect('list_albums')
    return render(request, 'core/home.html')


@login_required
def list_albums(request):
    albums = request.user.albums.all()
    form = AlbumForm()
    return render(request, 'core/list_albums.html', {'albums': albums, 'form':form})


@login_required
def list_photos(request):
    photos = request.user.photos.all()
    form = PhotoForm()
    return render(request, 'core/list_photos.html', {'photos': photos, 'form': form})


@login_required
def show_photo(request, pk):
    photo = get_object_or_404(request.user.photos, pk=pk)
    form = PhotoForm()
    photos = photo.photos.order_by('uploaded_at')
    user_favorite = request.user.is_favorite_photo(photo)
    return render(request, 'core/show_photo.html', {'photo': photo, 'form': form, 'photos': photos, 'user_favorite': user_favorite, 'pk':pk})
   

@login_required
def show_album(request, pk):
    album = get_object_or_404(request.user.albums, pk=pk)
    form = AlbumForm()
    photos = album.photos.all().order_by('uploaded_at')
    user_favorite = request.user.is_favorite_album(album)
    return render(request, 'core/show_album.html', {'album': album, 'pk': pk, 'form': form, 'photos': photos, 'user_favorite': user_favorite})


@login_required
def add_photo(request):
    if request.method == 'POST':
        form = PhotoForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.owner = request.user
            photo.save()
            return redirect(to='list_photos')
    else:
        form = PhotoForm()
    return render(request, 'core/add_photo.html', {'form': form})


@login_required
def add_album(request):
    if request.method == 'POST':
        form = AlbumForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            album = form.save(commit=False)
            album.owner = request.user
            album.save()
            return redirect(to='list_albums')
    else:
        form = AlbumForm()
    return render(request, 'core/add_album.html', {'form': form})


@login_required
def add_photo_to_album(request, pk):
    album = get_object_or_404(request.user.albums, pk=pk)
    photos = request.user.photos.exclude(albums__pk=album.pk)

    if request.method == 'POST':
        form = PhotoForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            photo = form.instance
            photo.owner = request.user
            photo.album = album
            photo.save()
            album.photos.add(photo)
        
            return redirect(to='show_album', pk=pk)
    else:
        form = PhotoForm()
    
    return render(request, 'core/add_photo_to_album.html', {'form': form, 'album': album, 'photos': photos})


@login_required
def edit_album(request, pk):
    album = get_object_or_404(request.user.albums, pk=pk)
    if request.method == 'POST':
        form = AlbumForm(data=request.POST, instance=album)
        if form.is_valid():
            album = form.save()
            return redirect(to='list_albums')
    else:
        form = AlbumForm(instance=album)
    return render(request, 'core/edit_album.html', {'form': form, 'album': album})

@login_required
def delete_album(request, pk):
    album = get_object_or_404(request.user.albums, pk=pk)
    if request.method == 'POST':
        album.delete()
        messages.success(request, 'Album deleted.')
        return redirect(to='list_albums')

    return render(request, 'core/delete_album.html', {'album': album })


@login_required
def delete_photo(request, pk):
    photo = get_object_or_404(request.user.photos, pk=pk)
    if request.method == 'POST':
        photo.delete()
        messages.success(request, 'Photo deleted.')
        return redirect(to='list_photos')

    return render(request, 'core/delete_photo.html', {'photo': photo })


def search_photos(request):
    pass


@login_required
@csrf_exempt
@require_POST
def favorite_album(request, pk):
    album = get_object_or_404(request.user.albums, pk=pk)
    if album in request.user.favorite_album.all():
        request.user.favorite_album.remove(album)
        return JsonResponse({'favorite': False})
    else:
        request.user.favorite_album.add(album)
        return JsonResponse({'favorite': True})


@login_required
@csrf_exempt
@require_POST
def favorite_photo(request, pk):
    photo = get_object_or_404(request.user.photos, pk=pk)
    if photo in request.user.favorite_photos.all():
        request.user.favorite_photo.remove(photo)
        return JsonResponse({'favorite': False})
    else:
        request.user.favorite_photo.add(photo)
        return JsonResponse({'favorite': True})


@login_required
@csrf_exempt
def album_add_remove_photo(request):
    photo_pk = request.POST.get('pk')
    action = request.POST.get('action')
    album_pk = request.POST.get('album')

    album = request.user.albums.get(pk=album_pk)
    photo = request.user.photos.get(pk=photo_pk)

    if action == 'add':
        album.photos.add(photo)
    elif action == 'remove':
        album.photos.remove(photo)
    
    return HttpResponse(status=204)