import pandas as pd
import numpy
import requests
import json
import datetime

url = 'https://nflrankings.theringer.com/qb-rankings'

##########
## PULL ##
##########
def get_data():
    '''
    Gets the qb rankings page and a json object
    '''
    res = requests.get(url)
    ## split the page to get json they pass to script ##
    first = res.text.split('"application/json">')[1]
    second = first.split('</script>')[0]
    ## parse ##
    data = json.loads(second)
    ## get qb rankings ##
    qb_data = data['props']['pageProps']['qbRankings']['data']
    qb_page_meta = data['props']['pageProps']['pages']['qbRankings']
    return qb_page_meta, qb_data

#############
## HELPERS ##
#############
def safe_get(obj, search_array):
    '''
    Searches a multi level dict and returns null if missing
    '''
    for key in search_array:
        try:
            obj = obj[key]
        except:
            return numpy.nan
    ## if successfully iterred, return result ##
    return obj
    

def current_season():
    '''
    Infers season
    '''
    ## infer season ##
    current_month = datetime.datetime.now().month
    current_season = datetime.datetime.now().year
    if current_month <= 4:
        current_season = datetime.datetime.now().year - 1
    ## return ##
    return current_season

def parse_week(weekly_ranks):
    '''
    reads a dict of weekly ranks and parses the most recent
    '''
    vals =  []
    for week_str in weekly_ranks:
        ## split the week string and translate to num ##
        vals.append(int(week_str.split('_')[1]))
    ## return most recent ##
    return max(vals)

def parse_p(p_str):
    '''
    parses the text from an html p
    '''
    return p_str.split('<p>')[1].split('</p>')[0]

def parse_badges(badges):
    '''
    parses badges field and controls for none
    '''
    try:
        return ', '.join(badges)
    except:
        return numpy.nan

def parse_qb_json(qb_json, season):
    '''
    parses the qb json and returns structured record
    '''
    return {
        'grade_id' : '{0}-{1}-{2}'.format(
            season,
            parse_week(qb_json['weeklyRanks']),
            qb_json['shareId']
        ),
        'season' : season,
        'week' : parse_week(qb_json['weeklyRanks']),
        'qb_id' : qb_json['shareId'],
        'qb_name' : qb_json['name'],
        'qb_team' : qb_json['team'],
        'qb_age' : qb_json['age'],
        'qb_salary' : qb_json['salary'],
        'qb_pro_bowl' : safe_get(qb_json, ['resume', 'pro_bowls']),
        'qb_mvps' : safe_get(qb_json, ['resume', 'mvps']),
        'qb_sbs' : safe_get(qb_json, ['resume', 'rings']),
        'qb_rank' : qb_json['rank'],
        'qb_rank_epa' : safe_get(qb_json, ['ranks','epa','rank']),
        'qb_rank_success' : safe_get(qb_json, ['ranks','success','rank']),
        'qb_rank_cpoe' : safe_get(qb_json, ['ranks','cpoe','rank']),
        'qb_grade_overall' : qb_json['qb_grade'],
        'qb_grade_arm_talent' : qb_json['chart']['arm_talent'],
        'qb_grade_timing' : qb_json['chart']['timing'],
        'qb_grade_pocket_presence' : qb_json['chart']['pocket_presence'],
        'qb_grade_creativity' : qb_json['chart']['creativity'],
        'qb_grade_accuracy' : qb_json['chart']['accuracy'],
        'qb_grade_decision_making' : qb_json['chart']['decision_making'],
        'qb_badges' : parse_badges(qb_json['badges']),
        'qb_headline' : parse_p(qb_json['blurb']),
        'qb_strength' : safe_get(qb_json, ['strength', 'label']),
        'qb_strength_desc' : parse_p(qb_json['strength']['text']),
        'qb_weakness' : safe_get(qb_json, ['weakness', 'label']),
        'qb_weakness_desc' : parse_p(qb_json['weakness']['text']),
        'qb_image' : safe_get(qb_json, ['image','original']),
        'qb_headshot' : safe_get(qb_json, ['headshot','original']),
    }

def parse_qbs(qb_json):
    '''
    parses qb json and returns df
    '''
    season = current_season()
    records = []
    ## iter through qbs ##
    for k, v in qb_json.items():
        records.append(parse_qb_json(v, season))
    ## return ##
    return pd.DataFrame(records)

def get_qb_grades():
    '''
    wrapper that pulls qb grades and returns df
    '''
    meta, data = get_data()
    return parse_qbs(data)
