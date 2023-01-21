import streamlit as st
import pandas as pd
import optimize_team as ot
import expected_value as ev
import fetch_data as fd
import datetime


st.set_page_config(page_title="FPL-Optimizer",page_icon="https://fantasy.premierleague.com/img/favicons/favicon-32x32.png")


st.markdown(
    """
    <style>
    .pitch {
        background:url(https://fantasy.premierleague.com/static/media/pitch-default.dab51b01.svg);
          background-position: center top;
          background-size: 100%;
        background-repeat: no-repeat;
    }
    .row {
        text-align: center;
    }
    .row-out {
        background: linear-gradient(90deg, rgba(2,0,36,1) 0%, rgba(255,1,1,0.5838414634146342) 0%, rgba(255,255,255,1) 100%);
    }
    .row-in {
        background: linear-gradient(90deg, rgba(2,0,36,1) 0%, rgba(70,185,80,0.5838414634146342) 0%, rgba(255,255,255,1) 100%);
    }
    .subrow {
        text-align: center;
        background-color:rgba(114, 207, 159, 0.9);
    }
    .css-1n76uvr > div > .css-1n76uvr {
        background: #f7f6f5;
        margin: 5px 0px 0px 0px;
        border-radius: 5px;
    }
    .playercard {
      font-family: "PremierSans-Regular", Arial, "Helvetica Neue", Helvetica, "sans-serif";
        text-align: center;
        margin: auto;
        width: 18%;
        #border: 3px solid green;
        display:inline-block;
        font-size:min(2.5vw,20px);
        font-weight:bold;
    }
    .playercard > img {
        width: 40%;
    }
    .pname {
      background: #37003c;
        text-align: center;
        margin: auto;
      color: white;
      width: 90%;
    }
    .tout {
      background: #37003c;
        text-align: left;
        margin: auto;
      color: white;
    }
    .tin {
      background: #37003c;
        text-align: left;
        margin: auto;
      color: white;
    }
    .pteam {
      background: #46c584;
      text-align: center;
        margin: auto;
      border-radius:0px 0px 5px 5px;
      width: 90%;
    }
    </style>"""
    ,
    unsafe_allow_html=True
)

@st.cache(allow_output_mutation=True)
def fetch_data(inp):
    ctx = fd.create_connection()
    df = fd.fetch_data(ctx)
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


def generate_pitch(df):
    pitch = '<div class="pitch">'
    row = '<div class="row">'
    for k,each in df[df.status=="starting"][df.p_position==1].iterrows():
        row+= ' '.join([
        '<div class="playercard">',
        '<image src="' + each['shirt'] +'">',
        '<div class="pname">' + each['name'] + '</div>',
        '<div class="pteam">' + each['team_name'] + '</div>',
        '</div>'
        ])
    row+='</div>'
    pitch += row
    row = '<div class="row">'
    for k,each in df[df.status=="starting"][df.p_position==2].iterrows():
        row+= ' '.join([
        '<div class="playercard">',
        '<image src="' + each['shirt'] +'">',
        '<div class="pname">' + each['name'] + '</div>',
        '<div class="pteam">' + each['team_name'] + '</div>',
        '</div>'
        ])
    row+='</div>'
    pitch += row
    row = '<div class="row">'
    for k,each in df[df.status=="starting"][df.p_position==3].iterrows():
        row+= ' '.join([
        '<div class="playercard">',
        '<image src="' + each['shirt'] +'">',
        '<div class="pname">' + each['name'] + '</div>',
        '<div class="pteam">' + each['team_name'] + '</div>',
        '</div>'
        ])
    row+='</div>'
    pitch += row
    row = '<div class="row">'
    for k,each in df[df.status=="starting"][df.p_position==4].iterrows():
        row+= ' '.join([
        '<div class="playercard">',
        '<image src="' + each['shirt'] +'">',
        '<div class="pname">' + each['name'] + '</div>',
        '<div class="pteam">' + each['team_name'] + '</div>',
        '</div>'
        ])
    row+='</div>'
    pitch += row
    row = '<div class="subrow">'
    for k,each in df[df.status=="bench"].sort_values(["p_position"]).iterrows():
        row+= ' '.join([
        '<div class="playercard">',
        '<image src="' + each['shirt'] +'">',
        '<div class="pname">' + each['name'] + '</div>',
        '<div class="pteam">' + each['team_name'] + '</div>',
        '</div>'
        ])
    row+='</div>'
    pitch += row
    pitch += '</div>'
    return pitch


def generate_transfers(df):
    transfers = '<div>'
    row = '<div class="tout">Transfer out:</div><div class="row-out">'
    for k,each in df[df.choice=="transfer out"].iterrows():
        row+= ' '.join([
        '<div class="playercard">',
        '<image src="' + each['shirt'] +'">',
        '<div class="pname">' + each['name'] + '</div>',
        '<div class="pteam">' + each['team_name'] + '</div>',
        '</div>'
        ])
    row+='</div>'
    transfers += row
    row = '<div class="tin">Transfer in:</div><div class="row-in">'
    for k,each in df[df.choice=="transfer in"].iterrows():
        row+= ' '.join([
        '<div class="playercard">',
        '<image src="' + each['shirt'] +'">',
        '<div class="pname">' + each['name'] + '</div>',
        '<div class="pteam">' + each['team_name'] + '</div>',
        '</div>'
        ])
    row+='</div>'
    transfers += row
    transfers +='</div>'
    return transfers

    
df = fetch_data(30)
df.columns = [x.lower() for x in df.columns]
df['good_games'] = df['good_games'].astype(int)
df['now_cost'] = df['now_cost'].astype(int)
df['future_good_games'] = df.apply(lambda x: (x.good_games / max(df['good_games'])),axis=1)
prices = df['now_cost'] / 10
positions = df['p_position']
clubs = df['team_name']
names = df['name']



st.title('FPL team generator')
z = st.expander("Pick team:")

z.write("")
_,g1,g2,_ = z.columns([4,4,4,4])
_,d1,d2,_ = z.columns([1,10,4,1])
_,m1,m2,_ = z.columns([1,10,4,1])
_,f1,f2,_ = z.columns([2,8,4,2])
z.write("")
num1,num2 = z.columns(2)
btn = z.container()
y = st.expander("Choose expected source:")
evb = y.radio(
    "Expected value source",
    ('Custom 1gw', 'Custom 3gw', 'Custom 5gw', 'FPL-API'),
    horizontal=True)
if(evb=='Custom 1gw'):
    df['future_cs'] = df.apply(lambda x: x.cs_gw2, axis=1)
    df['future_eg'] = df.apply(lambda x: x.eg_gw2, axis=1)
    df['future_cs'] = df.apply(lambda x: (x.future_cs / max(df['future_cs'])),axis=1)
    df['future_eg'] = df.apply(lambda x: (x.future_eg / max(df['future_eg'])),axis=1)
    df['expected'] = df.apply(ev.expected_score, axis=1)
    expected_scores = df['expected']

elif(evb=='Custom 3gw'):
    df['future_cs'] = df.apply(lambda x: x.cs_gw2 + x.cs_gw3 + x.cs_gw4, axis=1)
    df['future_eg'] = df.apply(lambda x: x.eg_gw2 + x.eg_gw3 + x.eg_gw4, axis=1)
    df['future_cs'] = df.apply(lambda x: (x.future_cs / max(df['future_cs'])),axis=1)
    df['future_eg'] = df.apply(lambda x: (x.future_eg / max(df['future_eg'])),axis=1)
    df['expected'] = df.apply(ev.expected_score, axis=1)
    expected_scores = df['expected']

elif(evb=='Custom 5gw'):
    df['future_cs'] = df.apply(lambda x: x.cs_gw2 + x.cs_gw3 + x.cs_gw4 + x.cs_gw5 + x.cs_gw6 , axis=1)
    df['future_eg'] = df.apply(lambda x: x.eg_gw2 + x.eg_gw3 + x.eg_gw4 + x.cs_gw5 + x.cs_gw6 , axis=1)
    df['future_cs'] = df.apply(lambda x: (x.future_cs / max(df['future_cs'])),axis=1)
    df['future_eg'] = df.apply(lambda x: (x.future_eg / max(df['future_eg'])),axis=1)
    df['expected'] = df.apply(ev.expected_score, axis=1)
    expected_scores = df['expected']
elif(evb=='FPL-API'):
    df['expected'] = df['fpl_ept'] + df['fpl_epn']
    expected_scores = df['expected']


opt_btn = st.button("Generate optimal team")
v_pitch = st.container()


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
        #st.dataframe(res[["name","p_position","choice","status_x","captain","now_cost","total_points","expected"]].sort_values(['expected'],ascending = [False]))
        #st.dataframe(res)
        res = res.rename(columns={"status_x": "status"})
        pitch = generate_pitch(res)
        v_pitch.markdown(pitch,unsafe_allow_html=True)
        trans = generate_transfers(res)
        v_pitch.markdown(trans,unsafe_allow_html=True)



if(opt_btn):
    decisions, captain_decisions,sub_decisions = ot.select_team(
                                            expected_scores,
                                            prices,
                                            positions,
                                            clubs,
                                            [],
                                            [],
                                            15,
                                            100)
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
    res["captain"] = res.apply(lambda x: (x["name"]==captain and x["position"]== captain_pos),axis=1)
    res = res[res.status.isin(["starting","bench"])]
    pitch = generate_pitch(res)
    v_pitch.markdown(pitch,unsafe_allow_html=True)
