import pandas as pd


def expected_score(x):
    #Points for minutes played
    minutes = round(x.minutes/90)
    points = 0
    points += minutes
    if(x.element_type==1): #goalie
        points += (x.clean_sheets*4+(x.saves/3) - (x.goals_conceded/2)) * x.future_cs
    elif(x.element_type==2): #defender
        points += (x.clean_sheets*4 - (x.goals_conceded/2)) * x.future_cs
        points += (x.goals_scored*6 + x.assists*3) * x.future_eg
    elif(x.element_type==3): #midfielder
        points += x.clean_sheets * x.future_cs
        points += (x.goals_scored*5 + x.assists*3) * x.future_eg
    elif(x.element_type==4): #forward
        points += (x.goals_scored*3 + x.assists*3) * x.future_eg
    return ((points + x.total_points)/2) * (x.future_good_games+1)

