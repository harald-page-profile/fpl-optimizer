
import pandas as pd
import numpy as np
import requests
import urllib
import load_data as ld
import optimize_team as ot


def get_FPL_data():
    players = ld.get_play_data()
    cs = ld.get_cs_data()
    eg = ld.get_eg_data()

    t1 = list(set(eg['team']))
    t1.sort()
    t2 = list(set(players['team']))
    t2.sort()
    team_dim = pd.DataFrame(data = {'t1':t1, 't2':t2})
    eg.team = eg.team.replace(team_dim['t1'].values,team_dim['t2'].values)
    t1 = list(set(cs['team']))
    t1.sort()
    t2 = list(set(players['team']))
    t2.sort()
    team_dim = pd.DataFrame(data = {'t1':t1, 't2':t2})
    cs.team = cs.team.replace(team_dim['t1'].values,team_dim['t2'].values)
    df = pd.merge(players, eg, on = "team")
    df = pd.merge(df, cs, on = "team")
    #df = pd.merge(df,player_games, left_on='id', right_on='element')
    return df


df = get_FPL_data()
expected_scores = df['total_points']
prices = df['now_cost'] / 10
positions = df['element_type']
clubs = df['team_code']
names = df['web_name']



my_team = ['Haaland','Kane','Firmino',
          'Andreas','Trossard','Groß','Foden','Højbjerg',
          'Dier','Schär','Trippier','Cancelo','Castagne',
          'Pope','Sánchez']
my_team_pos = [4,4,4,
               3,3,3,3,3,
               2,2,2,2,2,
               1,1]
my_team_status = ['starting','starting','bench',
               'starting','starting','starting','starting','bench',
               'starting','starting','starting','starting','bench',
               'starting','bench']
my_team = pd.DataFrame(data = {'web_name': my_team,'element_type':my_team_pos,'status':my_team_status})
res = pd.merge(df,my_team,on = ["web_name","element_type"],how='left')
my_players = res.index[res.status_y.notnull()].tolist()
my_players = res.index[res.status_y=='starting'].tolist()
my_subs = res.index[res.status_y=='bench'].tolist()

res["display"] = res["web_name"] + " pos:" + res["element_type"].astype(str)


new = res["display"].str.split(" pos:", expand = True)
res["name"] = new[1]
print(res["name"])
exit(1)
my_team=['Firmino', 'Højbjerg', 'Castagne', 'Pope']
my_subs=['Haaland', 'Kane', 'Andreas', 'Trossard', 'Groß', 'Foden', 'Dier', 'Schär', 'Trippier', 'Cancelo', 'Pope']

decisions, captain_decisions, sub_decisions = ot.select_team(expected_scores,prices,positions,clubs,my_team,my_subs,2)



pred_start = [names[i] for i in range(df.shape[0]) if decisions[i].value()>0]
pred_subs = [names[i] for i in range(df.shape[0]) if sub_decisions[i].value()>0]
status = ["starting"]*len(pred_start) + ["bench"]*len(pred_subs)





pred_team = pd.DataFrame({"name": pred_start + pred_subs, "status":status})
df["name"] = df["web_name"]
pd.merge(pred_team,df, on="name")
