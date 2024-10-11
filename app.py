from util import *


def dashboard():
  st.subheader(":grey[ :material/subdirectory_arrow_right: Dashboard]",
               divider='rainbow')
  with st.container(border=True):
    card(ss.me)
  rdt = {}
  for ur in ss.users:
    nm = ss.users[ur]['name']
    if ur == ss.me:
      nm += '(me)'
    rdt[nm] = ss.users[ur]['ratings']
  st.plotly_chart(gen_rating_graph(rdt), use_container_width=True)
  rtd = []
  for u, d in ss.users.items():
    rtd.append({
        'Name': d['name'] if u != ss.me else d['name'] + '(me)',
        'Rating': d['rating'],
        'Max Rating': d['maxRating'],
        'Rank': d['rank'],
        'Max Rank': d['maxRank']
    })
  rtd = pd.DataFrame(rtd)
  st.dataframe(rtd, use_container_width=True)

  dt = {}
  for ur in ss.users:
    nm = ss.users[ur]['name']
    if ur == ss.me:
      nm += '(me)'
    dt[nm] = {}
    for p in ss.users[ur]['problems']:
      if ss.users[ur]['problems'][p]:
        rt = int(ss.problems.loc[p]['rating'])
        if rt not in dt[nm]:
          dt[nm][rt] = 1
        else:
          dt[nm][rt] += 1
  st.plotly_chart(gen_pro_bar(dt), use_container_width=True)
  dtdf = pd.DataFrame(dt).T.fillna(0)
  dtdf['Total'] = dtdf.sum(axis=1)
  dtdf = dtdf.reset_index().rename(columns={'index': 'Name'})
  st.dataframe(dtdf, use_container_width=True)


if __name__ == '__main__':
  if not os.path.exists('problems.json'):
    with open('problems.json', 'w') as f:
      f.write('{}')
  if not os.path.exists('users.json'):
    getme()
  else:
    if 'loaded' not in ss:
      with st.spinner('Loading session'):
        log.info('Starting CodeMate')
        load_session()
    l, r = st.columns([9, 1])
    l.title(':violet[CodeMate]')
    r.write(' ')
    if r.button(':material/update:', key='update', type='primary'):
      update()
    nav = st.navigation({
        'CodeMate': [
            st.Page(dashboard,
                    title='Dashboard',
                    icon=':material/dashboard:',
                    default=True),
            st.Page('c2_ladders.py',
                    title='C2 Ladders',
                    icon=':material/assignment:'),
            st.Page("profile.py",
                    title='Profile',
                    icon=':material/account_box:'),
            st.Page('settings.py',
                    title='Settings',
                    icon=':material/settings:'),
            st.Page('temp.py',)
        ]
    })
    nav.run()
