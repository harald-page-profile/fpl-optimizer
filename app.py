import streamlit as st
import pandas as pd
import optimize_team as ot
import expected_value as ev
import fetch_data as fd
import datetime


#https://fantasy.premierleague.com/img/favicons/favicon-32x32.png

st.markdown(
    """
    <style>
    .css-1n76uvr > div > .css-1n76uvr {
        background: #f7f6f5;
        #background-image: url("https://static.vecteezy.com/system/resources/previews/003/715/625/original/football-field-or-soccer-field-background-green-grass-court-for-create-soccer-game-vector.jpg");
        margin: 5px 0px 0px 0px;
        border-radius: 5px;
    }</style>"""
    ,
    unsafe_allow_html=True
)

@st.cache(allow_output_mutation=True)
def fetch_data(inp):
    ctx = fd.create_connection()
    df = fd.fetch_data(ctx)
    print(df.head(10))
    return df
    

def filter_choices(x):
    if(x.status_x in ["starting","bench"] and x.status_y not in ["starting","bench"]):
        return "transfer in"
    elif(x.status_x in ["starting","bench"] and x.status_y in ["starting","bench"]):
        return "keep"
    elif(x.status_y in ["starting","bench"]):
        return "transfer out"
    else:
        return "not in team"

    
df = fetch_data(datetime.datetime.now().date())
df.columns = [x.lower() for x in df.columns]
df['good_games'] = df['good_games'].astype(int)
df['now_cost'] = df['now_cost'].astype(int)

df['future_cs'] = df.apply(lambda x: x.cs_gw2 + x.cs_gw3 + x.cs_gw4, axis=1)
df['future_eg'] = df.apply(lambda x: x.eg_gw2 + x.eg_gw3 + x.eg_gw4, axis=1)
df['future_cs'] = df.apply(lambda x: (x.future_cs / max(df['future_cs'])),axis=1)
df['future_eg'] = df.apply(lambda x: (x.future_eg / max(df['future_eg'])),axis=1)
df['future_good_games'] = df.apply(lambda x: (x.good_games / max(df['good_games'])),axis=1)
prices = df['now_cost'] / 10
positions = df['p_position']
clubs = df['team_name']
names = df['name']
df['expected'] = df.apply(ev.expected_score, axis=1)
expected_scores = df['expected']




st.title('FPL team generator')

z = st.container()

z.write("")
_,g1,g2,_ = z.columns([4,4,4,4])
_,d1,d2,_ = z.columns([1,10,4,1])
_,m1,m2,_ = z.columns([1,10,4,1])
_,f1,f2,_ = z.columns([2,8,4,2])
z.write("")
num1,num2,btn = st.columns(3)


stg = g1.multiselect("Starting goalie",list(df[df.p_position==1].name))
sug = g2.multiselect("Sub goalie",[each for each in df[df.p_position==1].name if each not in stg])

std = d1.multiselect("Starting defenders",list(df[df.p_position==2].name))
sud = d2.multiselect("Sub defenders",[each for each in df[df.p_position==2].name if each not in std])

stm = m1.multiselect("Starting midfielders",list(df[df.p_position==3].name))
sum = m2.multiselect("Sub midfielders",[each for each in df[df.p_position==3].name if each not in stm])

stf = f1.multiselect("Starting forwards",list(df[df.p_position==4].name))
suf = f2.multiselect("Sub forwards",[each for each in df[df.p_position==4].name if each not in stf])

_names = stg + sug + std + sud + stm + sum + stf + suf
_positions = ([1] * len(stg + sug)) + \
            ([2] * len(std + sud)) + \
            ([3] * len(stm + sum)) + \
            ([4] * len(stf + suf))
_statuses = (["starting"] * len(stg)) + (["bench"] * len(sug)) + \
            (["starting"] * len(std)) + (["bench"] * len(sud)) + \
            (["starting"] * len(stm)) + (["bench"] * len(sum)) + \
            (["starting"] * len(stf)) + (["bench"] * len(suf))

#st.dataframe(select_df)

if(len(set(stg + sug))==2 and len(set(std + sud))==5 and len(set(stm + sum))==5 and len(set(stf + suf))==3):

    team_df = pd.DataFrame({"name":_names,"position":_positions,"status":_statuses})
    select_df = pd.merge(df,team_df,how='left',
            left_on=["p_position","name"],
            right_on=["position","name"])
    my_players = select_df.index[select_df.status=='starting'].tolist()
    my_subs = select_df.index[select_df.status=='bench'].tolist()



    nsubs = num1.number_input('Choose number of transfers',value=1)
    budget = num2.number_input('Choose budget in millions',value=100)
    press = btn.button("Generate Team!")
    if(press):
        decisions, captain_decisions,sub_decisions = ot.select_team(
                                                expected_scores,
                                                prices,
                                                positions,
                                                clubs,
                                                my_players,
                                                my_subs,
                                                nsubs,
                                                budget)
        pred_start = [names[i] for i in range(df.shape[0]) if decisions[i].value()>0]
        pred_subs = [names[i] for i in range(df.shape[0]) if sub_decisions[i].value()>0]
        pred_pos = [positions[i] for i in range(df.shape[0]) if decisions[i].value()>0]
        pred_pos += [positions[i] for i in range(df.shape[0]) if sub_decisions[i].value()>0]
        captain = [names[i] for i in range(df.shape[0]) if captain_decisions[i].value()>0][0]
        captain_pos = [positions[i] for i in range(df.shape[0]) if captain_decisions[i].value()>0][0]
        status = ["starting"]*len(pred_start) + ["bench"]*len(pred_subs)
        pred_team = pd.DataFrame({"name": pred_start + pred_subs,
                                "status":status,
                                "position":pred_pos})
        pred_team['position']=pred_team['position'].astype(int)
        res = pd.merge(df, pred_team,how='left', left_on = ["name","p_position"], right_on=["name","position"])
        res["now_cost"] = res["now_cost"]/10
        res = pd.merge(res,team_df,how='left', left_on = ["name","p_position"], right_on=["name","position"])
        res["choice"] = res.apply(filter_choices, axis=1)
        res["captain"] = res.apply(lambda x: (x["name"]==captain and x["position_x"]== captain_pos),axis=1)
        res = res[res.choice.isin(["transfer in","transfer out","keep"])]
        st.dataframe(res[["name","p_position","choice","status_x","captain","now_cost","total_points","expected"]].sort_values(['expected'],ascending = [False]))
