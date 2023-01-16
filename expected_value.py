import pandas as pd


def expected_score(x):
    #Points for minutes played
    minutes = round(x.minutes/90)
    points = 0
    points += minutes
    if(x.p_position==1): #goalie
        points += float(x.clean_sheets*4+(x.saves/3) - (x.goals_conceded/2)) * x.future_cs
    elif(x.p_position==2): #defender
        points += float(x.clean_sheets*4 - (x.goals_conceded/2)) * x.future_cs
        points += float(x.goals_scored*6 + x.assists*3) * x.future_eg
    elif(x.p_position==3): #midfielder
        points += float(x.clean_sheets) * x.future_cs
        points += float(x.goals_scored*5 + x.assists*3) * x.future_eg
    elif(x.p_position==4): #forward
        points += float(x.goals_scored*3 + x.assists*3) * x.future_eg
    return float((points + float(x.total_points)/2)) * (x.future_good_games+1)

