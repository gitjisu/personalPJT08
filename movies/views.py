from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.views.decorators.http import require_safe
from django.http import JsonResponse, HttpResponse
from .models import Movie
import requests
import random

# Create your views here.
@require_safe
def index(request):
    movies = Movie.objects.order_by('-pk')
    context = {
        'movies': movies,
    }
    return render(request, 'movies/index.html', context)
    


@require_safe
def detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    context = {
        'movie' : movie
    }
    return render(request, 'movies/detail.html', context)




@require_safe
def recommended(request):
    names = ['대부','스파이더맨','인셉션','노트북','행오버']
    name = random.choice(names)
    if name == '대부' :
        genre = '범죄,스릴러'
    elif name == '스파이더맨' :
        genre = '액션, 슈퍼히어로'
    elif name == '인셉션' :
        genre = 'SF,스릴러' 
    elif name == '노트북' :
        genre = '로맨스,멜로'
    elif name == '행오버' :
        genre = '코미디,드라마'
    ids=[]
    BASE_URL='https://api.themoviedb.org/3'
    path='/search/movie'
    params = {
        'api_key' : '9d7cb51587fb0d8a745072f31125be0f',
        'language' : 'ko',
        'query' : f'{name}'
    }
    response = requests.get(BASE_URL+path, params=params)
    data = response.json()
    for i in data['results']:
        ids.append(i["id"])      
    recommendations=[]  
    for movie_id in ids :    
        BASE_URL='https://api.themoviedb.org/3'
        path=f'/movie/{movie_id}/recommendations'
        params = {
            'api_key' : '9d7cb51587fb0d8a745072f31125be0f',
            'language' : 'ko',
        }
        response = requests.get(BASE_URL+path, params=params)
        data = response.json()
        for i in data['results'] :
            recommendations.append(i)
    movies=random.sample(recommendations,10)
    # poster_url=movie['poster_path']
    poster=f'https://image.tmdb.org/t/p/w500'
    # title=movie['title']
    # vote_average=movie['vote_average']
    # overview=movie['overview']
    # release_date=movie['release_date']
    # context={
    #     'poster' : poster,
    #     'title' : title,
    #     'vote_average' : vote_average,
    #     'overview' : overview,
    #     'release_date' : release_date,
    # }
    context = {
        'movies' : movies,
        'poster' : poster,
        'genre' : genre,
    }
    return render(request, 'movies/recommended.html', context)

