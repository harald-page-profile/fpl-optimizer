import streamlit as st
import pandas as pd
import numpy as np
import requests
import urllib
import datetime
import load_data as ld
import optimize_team as ot
import expected_value as ev

st.title('FPL team generator')

#default_starters = []
default_starters = ['Pope pos:1', 'Dier pos:2', 'Schär pos:2', 'Trippier pos:2', 'Cancelo pos:2', 'Andreas pos:3', 'Trossard pos:3', 'Saka pos:3', 'Foden pos:3', 'Haaland pos:4', 'Kane pos:4']
#default_subs = []
default_subs = ['Sánchez pos:1', 'Edouard pos:4', 'Castagne pos:2', 'Højbjerg pos:3']

@st.cache(allow_output_mutation=True)
def get_FPL_data(current_date):
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
    
    ids = [each for each in players['id']]
    player_games = ld.get_game_history(ids)
    df = pd.merge(df,player_games, left_on='id', right_on='element')
    
    return df

def highlight_players(s,cap):
    return ['background-color: lightgreen']*len(s) if s.Name==cap else ['']*len(s)

col1,col2 = st.columns(2)

try:
    df = get_FPL_data(datetime.date(2022, 1, 1))
    #df = get_FPL_data(datetime.datetime.now().date())
    df['future_cs'] = df.apply(lambda x: x.cs_gw2 + x.cs_gw3 + x.cs_gw4, axis=1)
    df['future_eg'] = df.apply(lambda x: x.gw2 + x.gw3 + x.gw4, axis=1)
    df['future_cs'] = df.apply(lambda x: (x.future_cs / max(df['future_cs'])),axis=1)
    df['future_eg'] = df.apply(lambda x: (x.future_eg / max(df['future_eg'])),axis=1)
    df['future_good_games'] = df.apply(lambda x: (x.good_games / max(df['good_games'])),axis=1)
    prices = df['now_cost'] / 10
    positions = df['element_type']
    clubs = df['team_code']
    names = df['web_name']
    
    df['display'] = df["web_name"] + " pos:" + df["element_type"].astype(str)
    
    players = col1.multiselect(
        "Choose your starters", list(df.display), default = default_starters
    )
    sub_players = col2.multiselect(
        "Choose your subs", list(df.display), default = default_subs
    )
    if len(set(players + sub_players))!=15:
        st.info("Please select a full team of players")
    else:
        df['expected'] = df.apply(ev.expected_score, axis=1)
        expected_scores = df['expected']
    
        num1,num2 = st.columns(2)
        nsubs = num1.number_input('Choose number of subs',value=1)
        budget = num2.number_input('Choose budget in millions',value=100)
        my_team = pd.DataFrame(data = {'display': players + sub_players,'status':(["starting"]*len(players)) + (["bench"]*len(sub_players))})

        _team = pd.merge(df,my_team,on = "display",how='left')
        my_players = _team.index[_team.status_y=='starting'].tolist()
        my_subs = _team.index[_team.status_y=='bench'].tolist()

        if st.button('Create optimized team'):
        
            decisions, captain_decisions, sub_decisions = ot.select_team(expected_scores,prices,positions,clubs,
                               my_players,my_subs,nsubs,budget)
                               
            
            pred_start = [names[i] for i in range(df.shape[0]) if decisions[i].value()>0]
            pred_subs = [names[i] for i in range(df.shape[0]) if sub_decisions[i].value()>0]
            pred_pos = [positions[i] for i in range(df.shape[0]) if decisions[i].value()>0]
            pred_pos += [positions[i] for i in range(df.shape[0]) if sub_decisions[i].value()>0]
            captain = [names[i] for i in range(df.shape[0]) if captain_decisions[i].value()>0][0]
            status = ["starting"]*len(pred_start) + ["bench"]*len(pred_subs)
            pred_team = pd.DataFrame({"name": pred_start + pred_subs,
                                    "status":status, "position":pred_pos})
            res = pd.merge(pred_team, df, left_on = ["name","position"], right_on=["web_name","element_type"])
            res["now_cost"] = res["now_cost"]/10
            tr_in = [p for p in res[res.status_x.isin(['starting','bench'])]['display'].values if p not in (players + sub_players)]
            tr_out = [p for p in (players + sub_players) if p not in res[res.status_x.isin(['starting','bench'])]['display'].values]

            print(res[res.status_x.isin(['starting','bench'])])


            res = res[["name","status_x",'gw2','cs_gw2','gw3','cs_gw3',
                        'gw4','cs_gw4',"good_games","position","now_cost","total_points","team"]]
            res.columns.values[0:8] = ["Name","Status","EG W+1","ECS W+1",
                                    "EG W+2","ECS W+2","EG W+3","ECS W+3"]
            
            res = res[["Name","Status","EG W+1","ECS W+1","EG W+2","ECS W+2",
            "good_games","position","now_cost","total_points","team"]]
            res = res.sort_values(['Status', 'total_points'],ascending = [False, False])
            st.dataframe(res.style.apply(highlight_players,cap=captain, axis=1))
            st.text("Transfer in: " + ", ".join(tr_in))
            st.text("Transfer out: " + ", ".join(tr_out))
            
except:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
    """
)
