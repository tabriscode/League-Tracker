from django.shortcuts import render
from django.http import HttpResponse
from riotwatcher import LolWatcher, ApiError
import math

from storefront.settings import RIOT_API_KEY
# Create your views here.
#request -> response
#request handler
#action


def index(request):
    return render(request, 'index.html')

def error(request):
    return render(request, 'error.html')

def get_summoner(request):
    summonername = request.GET.get('summonername')
    region = request.GET.get('region')
    queuetype = request.GET.get('queuetype')
    if region == 'NA1':
        route = 'AMERICAS'
    elif region == 'EUN1':
        route = 'EUROPE'
    elif region == 'EUW1':
        route = 'EUROPE'
    elif region == 'KR':
        route = 'ASIA'

    if queuetype == 'ranked_solo':
        queuetype = 420
    elif queuetype == 'ranked_flex':
        queuetype = 440
    elif queuetype == 'normal_blind':
        queuetype = 430
    elif queuetype == 'normal_draft':
        queuetype = 400
    elif queuetype == 'aram':
        queuetype = 450

    context = calculate(summonername, region, route, queuetype)
    return render(request, 'information.html', context)

#Grabs Riot Games API Key
#def get_API_key():
#    f = open("Riot_api_key.txt", "r")
#   return f.read()

def get_matches(summonername, region, route, queuetype, lol_watcher):
    uid = lol_watcher.summoner.by_name(region, summonername)
    puuid = uid['puuid']
    previous_match_ids = lol_watcher.match.matchlist_by_puuid(route #my_region_route 
                                                         ,puuid #puuid 
                                                         ,0 
                                                         ,10 #total_matches
                                                         ,queuetype #queue_type 
                                                         ,None ,None ,None )
    return previous_match_ids

def calculate(summonername, region, route, queuetype):
    lol_watcher = LolWatcher(RIOT_API_KEY)
    total_duration = 0
    total_gold = 0
    cspm = 0
    total_dead_time = 0
    match_ids = get_matches(summonername, region, route, queuetype, lol_watcher)
    for i in range(len(match_ids)):
        x = lol_watcher.match.by_id(route, match_ids[i])
        total_duration += x['info']['gameDuration']
        for increment in range(10):
            if summonername == x['info']['participants'][increment]['summonerName']:
                prefix = x['info']['participants'][increment]
                total_gold += prefix['goldEarned'] / (x['info']['gameDuration'] / 60)
                cspm += prefix['totalMinionsKilled'] / (x['info']['gameDuration'] / 60)
                total_dead_time += prefix['totalTimeSpentDead']

    #Grabs all matches, picks specific summoner_name's stats to look at
    #print(f'\nStats averaged for the past {total_matches} games')
    average_duration = math.trunc(total_duration / 60 / 10 ) #total_matches
    #print("Average game duration (minutes):", total_duration)
    cspm = round(cspm / 10, 2) #total matches
    #print("Average CSPM (Creep Score per minute):", cspm)
    gpm = round(total_gold / 10, 2) #total matches
    #print("Average Gold Earned:", total_gold)
    average_minutes_dead = math.trunc(total_dead_time / 10 / 60)
    average_seconds_dead = math.trunc(total_dead_time / 10 % 60)
    context = {
        'summonername': summonername,
        'region': region,
        'average_duration': average_duration,
        'cspm': cspm,
        'gpm': gpm,
        'average_minutes_dead': average_minutes_dead,
        'average_seconds_dead': average_seconds_dead
    }
    return context
    
