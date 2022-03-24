from django.shortcuts import render
from django.http import HttpResponse
from riotwatcher import LolWatcher, ApiError
import math
# Create your views here.
#request -> response
#request handler
#action

def index(request):
    return render(request, 'index.html')

def get_summoner(request):
    summonername = request.GET.get('summonername')
    region = request.GET.get('region')
    queuetype = request.GET.get('queuetype')
    if region == 'NA':
        route = 'AMERICAS'
    elif region == 'EUN':
        route = 'EUROPE'
    elif region == 'EUW':
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
def get_API_key():
    f = open("Riot_api_key.txt", "r")
    return f.read()

def get_matches(summonername, region, route, queuetype, lol_watcher):
    uid = lol_watcher.summoner.by_name(region, summonername)
    puuid = uid['puuid']
    previous_match_ids = lol_watcher.match.matchlist_by_puuid(route #my_region_route 
                                                         ,puuid #puuid 
                                                         ,0 
                                                         ,20 #total_matches
                                                         ,queuetype #queue_type 
                                                         ,None ,None ,None )
    return previous_match_ids

def calculate(summonername, region, route, queuetype):
    lol_watcher = LolWatcher(get_API_key())
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
    average_duration = math.trunc(total_duration / 60 / 20 ) #total_matches
    #print("Average game duration (minutes):", total_duration)
    cspm = round(cspm / 20, 2) #total matches
    #print("Average CSPM (Creep Score per minute):", cspm)
    gpm = round(total_gold / 20, 2) #total matches
    #print("Average Gold Earned:", total_gold)
    average_minutes_dead = math.trunc(total_dead_time / 20 / 60)
    average_seconds_dead = math.trunc(total_dead_time / 20 % 60)
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
    
