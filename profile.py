from util import *

if 'profile' not in ss:
  ss.profile = {}
  ss.profile['user'] = ss.users[ss.me]['name']+'(me)'

user = ss.profile['user']

st.subheader(
    ":grey[ :material/subdirectory_arrow_right: Profiles]", divider='rainbow')
users = {ss.users[i]['name']: i for i in ss.users if i != ss.me}
users = {ss.users[ss.me]['name']+'(me)': ss.me, **users}

user = st.selectbox(
    "Select User",
    users,
    index=list(users).index(user),
)
user = users[user]

with st.container(border=True):
  card(user)

rtdt = {}
tgdt = {}

for pro in ss.users[user]['problems']:
  if ss.users[user]['problems'][pro]:
    rt = int(ss.problems.loc[pro]['rating'])
    if rt not in rtdt:
      rtdt[rt] = 1
    else:
      rtdt[rt] += 1
    for tag in ss.problems.loc[pro]['tags']:
      if tag not in tgdt:
        tgdt[tag] = 1
      else:
        tgdt[tag] += 1


fig1 = go.Figure(data=[go.Bar(
    x=list(rtdt.keys()),
    y=list(rtdt.values()),
    text=list(rtdt.values()),
    textposition='auto',
)])
fig1.update_layout(
    title="<b>Problems and rating graph</b>",
    xaxis_title="<b>Difficulty Level</b>",
    yaxis_title="<b>Number of Problems</b>",
)
st.plotly_chart(fig1)


lb = list(tgdt.keys())
val = list(tgdt.values())

fig2 = go.Figure(
    data=[go.Pie(
        labels=lb,
        values=val,
        hole=0.5,  # Creates a donut chart
        textinfo='label+value'
    )]
)
fig2.update_layout(
    title="Problem Count by Tags",
)
st.plotly_chart(fig2)

if ss.me == user:
  st.subheader("Today's Solved Problems")


solved = [x for x in ss.users[user]['problems']
          if ss.users[user]['problems'][x]]
st.subheader(f"Solved Problems: {len(solved)}", divider='grey')
gen_df(solved, 'solved')

upsolved = [x for x in ss.users[user]['problems']
            if not ss.users[user]['problems'][x]]
st.subheader(f"Upsolve Problems: {len(upsolved)}", divider='grey')
gen_df(upsolved, 'upsolved')

ss.problems
