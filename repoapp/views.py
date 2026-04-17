import requests
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    context = {}
    
    if request.method == 'POST':
        username = request.POST.get('username')
        
        # GitHub API
        url = f'https://api.github.com/users/{username}/repos?per_page=100'
        repos = requests.get(url).json()
        
        user_data = requests.get(
            f'https://api.github.com/users/{username}'
        ).json()
        
        repo_list = []
        lang_count = {}
        
        for repo in repos:
            lang = repo.get('language') or 'Unknown'
            repo_list.append({
                'name': repo['name'],
                'link': repo['html_url'],
                'language': lang,
                'forked': repo['fork'],
                'date': repo['updated_at'][:10],
            })
            lang_count[lang] = lang_count.get(lang, 0) + 1
        
        # CSV Download
        if 'download' in request.POST:
            df = pd.DataFrame(repo_list)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{username}_repos.csv"'
            df.to_csv(response, index=False)
            return response
        
        context = {
            'repos': repo_list,
            'owner': user_data.get('name', username),
            'total': len(repo_list),
            'lang_count': lang_count,
            'username': username,
        }
    
    return render(request, 'index.html', context)