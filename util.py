import streamlit as st
import json
import coloredlogs
import logging
import requests
import time
from datetime import datetime
import pandas as pd
import os
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import random

ss = st.session_state


coloredlogs.install(
    level='DEBUG',
    fmt='%(asctime)s → %(message)s',
    level_styles={
        'debug': {'color': 'magenta'},
        'info': {'color': 'green'},
        'warning': {'color': 'yellow'},
        'error': {'color': 'red', 'bold': True},
        'critical': {'color': 'red', 'bold': True, 'background': 'yellow'}
    },
    field_styles={
        'asctime': {'color': 'cyan'},
        'hostname': {'color': 'magenta'},
        'name': {'color': 'cyan'},
        'levelname': {'bold': True, 'color': 'black'}
    }
)


log = logging

col = [
    "#bd93f9", "#ff79c6", "#8be9fd", "#50fa7b", "#ffb86c", "#ff5555", "#f1fa8c", "#6272a4", "#ff6e6e", "#69ff94",
    "#ff6347", "#ffa07a", "#20b2aa", "#87cefa", "#778899", "#b0c4de", "#32cd32", "#ff4500", "#da70d6", "#eee8aa",
    "#ff1493", "#00ced1", "#9400d3", "#ff8c00", "#00fa9a", "#4682b4", "#d2691e", "#ff00ff", "#7fffd4", "#dc143c",
    "#00bfff", "#ffdab9", "#8a2be2", "#5f9ea0", "#d2b48c", "#ffdead", "#ff69b4", "#cd5c5c", "#4b0082", "#7cfc00"
]
random.shuffle(col)


def toupdate(tm, hrs):
  return abs(tm - time.time())//3600 > hrs


# app


def load_session():
  log.info('Loading session')
  with open('users.json', 'r') as f:
    usersf = json.load(f)
  ss.me = usersf['me']
  ss.users = usersf['users']


  def ff(x, fl):
    rt = []
    for ur, dt in ss.users.items():
        if x.name in dt['problems'] and dt['problems'][x.name] == fl:
          rt.append(ur)
    return rt
  
  with open('problems.json', 'r') as f:
    pb = json.load(f)
    pbdf = pd.DataFrame.from_dict(pb, orient='index')
    # pbdf[['solved', 'upsolve']] = pbdf.apply(ff, axis=1)
    pbdf['solved'] = pbdf.apply(lambda x: ff(x, True), axis=1)
    pbdf['upsolve'] = pbdf.apply(lambda x: ff(x, False), axis=1)
    ss.problems = pbdf
  with open('c2dt.json', 'r') as f:
    c2 = json.load(f)
    for key in c2.keys():
      c2[key] = pd.DataFrame(c2[key])
    ss.c2 = c2
  ss.loaded = True
  with open('log.json', 'r') as f:
    lt = json.load(f)['timestamp']
    if toupdate(lt, 2):
      update()
  log.info('Session loaded')


def update(upusers=None, me=None):
  if upusers is None:
    upusers = ss.users.keys()
  if me is None:
    me = ss.me
  log.info('Updating')
  with st.status('Updating...', expanded=True):
    log.info('Loading existing problems and users data')
    with st.spinner("Loading existing problems and users data"):
      with open('problems.json') as p:
        problems = json.load(p)
      with open('users.json') as u:
        userf = json.load(u)
      users = userf['users']
    log.info('Fetching data from Codeforces')
    with st.spinner("Fetching data from Codeforces"):
      responses = []
      ruserra = {}
      ruserin = []
      pfl = False
      ufl = False
      td = datetime.now().date()
      c = 0
      while True:
        if c > 100:
          log.error('Failed to fetch data from Codeforces')
          st.error('Failed to fetch data from Codeforces')
          return
        try:
          response = requests.get(
              f"https://codeforces.com/api/user.info?handles={';'.join(upusers)}").json()
          if response['status'] == 'OK':
            ruserin = response['result']
            break
        except:
          c += 1
      for user in upusers:
        while True:
          try:
            response = requests.get(
                f'https://codeforces.com/api/user.status?handle={user}').json()
            if response['status'] == 'OK':
              responses.extend(response['result'])
              break
          except:
            pass
        while True:
          try:
            log.info('1')
            response = requests.get(
                f"https://codeforces.com/api/user.rating?handle={user}").json()
            if response['status'] == 'OK':
              ruserra[user] = response['result']
              break
          except Exception as e:
            print(e)
    log.info("Processing data")
    with st.spinner("Processing data"):
      for res in responses:
        id = f"{res['contestId']}/{res['problem']['index']}"
        for ur in [res['author']['members'][i]['handle'] for i in range(len(res['author']['members']))]:
          if ur not in users:
            continue
          if id not in problems:
            pfl = True
            problems[id] = {
                'name': res['problem']['name'],
                'rating': res['problem'].get('rating', 700),
                'tags': res['problem']['tags'],
            }
            users[ur]['problems'][id] = True if res['verdict'] == 'OK' else False
          elif id not in users[ur]['problems']:
            ufl = True
            users[ur]['problems'][id] = True if res['verdict'] == 'OK' else False
          elif users[ur]['problems'][id] == False:
            ufl = True
            users[ur]['problems'][id] = True if res['verdict'] == 'OK' else False
          if ur == me and users[ur]['problems'][id] and datetime.fromtimestamp(res['creationTimeSeconds']).date() == td:
            try:
              users[ur]['today'].append(id)
            except KeyError:
              users[ur]['today'] = [id]
      for ur in upusers:
        users[ur]['ratings'] = ruserra[ur]
      for ru in ruserin:
        users[ru['handle']]['rating'] = ru['rating']
        users[ru['handle']]['maxRating'] = ru['maxRating']
        users[ru['handle']]['rank'] = ru['rank']
        users[ru['handle']]['maxRank'] = ru['maxRank']
        users[ru['handle']]['friends'] = ru['friendOfCount']
        users[ru['handle']]['photo'] = ru['titlePhoto']
        users[ru['handle']]['lastOnline'] = datetime.fromtimestamp(
            ru['lastOnlineTimeSeconds']).strftime('%d-%m-%Y %H:%M:%S')
    log.info('Saving data')
    with st.spinner("Saving data"):
      if pfl:
        with open('problems.json', 'w') as p:
          json.dump(problems, p, indent=2)
      if ufl:
        with open('users.json', 'w') as u:
          json.dump({"me": me, "users": users}, u, indent=2)
    log.info('Data updated')
    with open('log.json', 'w') as f:
      json.dump({'timestamp': time.time()}, f)
    load_session()
    st.rerun()


@st.dialog("Enter your Codeforces handle")
def getme():
  with st.form(key='getme'):
    log.info('Creating user data')
    nm = st.text_input('Name')
    me = st.text_input('Handle')
    if st.form_submit_button('Submit', type='primary', use_container_width=True):
      with open('users.json', 'w') as f:
        json.dump({"me": me, "users": {
                  me: {'name': nm, 'problems': {}, 'today': {}}}}, f, indent=2)
      with open('problems.json', 'w') as f:
        json.dump({}, f)
      with open('log.json', 'w') as f:
        json.dump({'timestamp': time.time()}, f)
      log.info('User data created')
      load_session()
      update()
  if os.path.exists('users.json'):
    st.rerun()


def gen_rating_graph(data):
  fig = go.Figure()
  for handle, contests in data.items():
    ts = [datetime.fromtimestamp(item["ratingUpdateTimeSeconds"])
          for item in contests]
    ratings = [item["newRating"] for item in contests]
    htext = [f"""Handle: <b><i>{handle}</b></i><br>Contest: <b><i>{item['contestName']}</b></i><br>Rating: <b><i>{
        item['newRating']}</b></i><br>Rank: <b><i>{item['rank']}</b></i>"""for item in contests]
    fig.add_trace(go.Scatter(
        x=ts,
        y=ratings,
        mode='lines+markers',
        name=handle,
        hovertext=htext,
        hoverinfo="text"
    ))
  fig.update_layout(
      title="<b>Codeforces Rating</b>",
      xaxis_title="<b>Date</b>",
      yaxis_title="<b>Rating</b>",
      showlegend=True,
      legend=dict(
          title="<b>Users</b>",
      ),
  )
  return fig


def gen_pro_bar(data):
  fig = go.Figure()
  for i, (ur, pro) in enumerate(data.items()):
    dif = list(pro.keys())
    num = list(pro.values())
    fig.add_trace(go.Bar(
        x=dif,
        y=num,
        name=ur,
        text=[f"{ur}: <b>{num}</b>" for num in num],
        hoverinfo="text",
        # marker_color=col[i % len(col)]
    ))
  fig.update_layout(
      title="<b>Problems Solved</b>",
      xaxis_title="<b>Difficulty Level</b>",
      yaxis_title="<b>Number of Problems Solved</b>",
      barmode='group',
      legend_title="<b>Users</b>",
  )
  return fig


# c2_ladders


def color_tags(tags):
  ctags = {}
  cind = 0
  for tag in tags:
    ctags[tag] = col[cind % len(col)]
    cind += 1
  return ctags


def format_html(html_string):
  soup = BeautifulSoup(html_string, 'html.parser')
  return soup.prettify()


def gen_table(ladder, tags, show_tags=False):
  table = '''
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />
    <style>
      .round {
        display: inline-block;
        padding: 0.5em 1em;
        border-radius: 1em;
        color: white;
        margin: 0.2em;
      }
      table {
        width: 100%;
        border-collapse: collapse;
      }
      th, td {
        padding: 0.5em;
        text-align: left;
      }
      a {
        text-decoration: none;
        color: inherit;
      }
      .material-symbols-outlined {
        vertical-align: middle;
        font-variation-settings:
          'FILL' 0,
          'wght' 400,
          'GRAD' 0,
          'opsz' 24;
      }
      .solved {
        background-color: rgba(80, 250, 123, 0.2);
      }
      .not-solved {
        background-color: rgba(255, 85, 85, 0.2);
      }
    </style>
    <table border="1">
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Frequency</th>
          ''' + ('<th>Tags</th>' if show_tags else '') + '''
        </tr>
      </thead>
      <tbody>'''

  ladder.reset_index(drop=True, inplace=True)
  ladder.index = ladder.index

  for ind, pro in ladder.iterrows():
    table += f"""
    <tr class="{'solved' if pro['status'] == 'Solved' else 'not-solved' if pro['status'] == 'Upsolved' else ''}">
        <td>{ind + 1}</td>
        <td>
        <a href="https://codeforces.com/problemset/problem/{pro['id']}" target="_blank">
        {pro['name']}
        </a>
        </td>
        <td>{pro['frequency']}</td>{f'''<td>{''.join([fr'<span class="round" style="background-color: {tags[tag]}"> {tag}</span>' for tag in pro['tags']])}''' if show_tags else ''}
    </tr>
    """

  table += """
      </tbody>
    </table>
    """
  return format_html(table)


# profile
def gen_df(df, key):
  df = ss.problems.loc[df].reset_index().rename(columns={'index': 'id'})
  df['link'] = df['id'].apply(
      lambda x: f"https://codeforces.com/problemset/problem/{x}")
  df.drop(columns=['id'], inplace=True)
  df.index = df.index + 1
  df.columns = df.columns.str.capitalize()
  st.data_editor(
      df,
      disabled=df.columns,
      column_config={
          'Link': st.column_config.LinkColumn()
      },
      key=key
  )


# settings


@st.dialog("Update your profile")
def updateme():
  with st.form(key='updateme'):
    log.info('Updating me')
    uu = {ss.users[u]['name']: u for u in ss.users}
    me = st.selectbox('Name', uu.keys(), index=list(
        uu.keys()).index(ss.users[ss.me]['name']))
    if st.form_submit_button('Submit', type='primary', use_container_width=True):
      with open('users.json', 'r') as f:
        usersf = json.load(f)
      usersf['me'] = uu[me]
      with open('users.json', 'w') as f:
        json.dump(usersf, f, indent=2)
      log.info('me updated')
      load_session()
      update()
      st.rerun()


def delfriend(friend):
  with open('users.json', 'r') as f:
    usersf = json.load(f)
  del usersf['users'][friend]
  with open('users.json', 'w') as f:
    json.dump(usersf, f, indent=2)
  log.info(f'Friend {friend} deleted')
  st.toast(f'Friend {friend} deleted')
  load_session()
  update()
  st.rerun()


@st.dialog("Enter your friend's Codeforces handle")
def addfriend():
  with st.form(key='addfriend'):
    log.info('Adding friend')
    nm = st.text_input('Name')
    fr = st.text_input('Handle')
    if st.form_submit_button('Submit', type='primary', use_container_width=True):
      with open('users.json', 'r') as f:
        usersf = json.load(f)
      usersf['users'][fr] = {'name': nm, 'problems': {}, 'today': {}}
      with open('users.json', 'w') as f:
        json.dump(usersf, f, indent=2)
      log.info(f'Friend {fr} added')
      st.toast(f'Friend {fr} added')
      load_session()
      update()
      st.rerun()


def card(user):
  l, r = st.columns([3, 2])
  with l:
    st.subheader(f":grey[Name:] ***{ss.users[user]['name']}***")
    st.subheader(
        f":grey[Handle:] ***[{user}](https://codeforces.com/profile/{user})***")
    st.subheader(
        f":grey[Rating:] ***{ss.users[user]['rating']}({ss.users[user]['maxRating']})***")
    st.subheader(
        f":grey[Rank:] ***{ss.users[user]['rank']}({ss.users[user]['maxRank']})***")
    st.subheader(
        f":grey[Friends:] ***{ss.users[user]['friends']}***")
  st.subheader(
      f":grey[Last Online:] ***{ss.users[user]['lastOnline']}***")
  with r:
    st.image(ss.users[user]['photo'], use_column_width=True)
