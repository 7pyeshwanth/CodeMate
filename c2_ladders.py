from util import *


if 'c2l' not in ss:
  log.info('Initializing C2 Ladders')
  ss['c2l'] = {}
  ss['c2l']['user'] = ss.users[ss.me]['name']+'(me)'
  ss['c2l']['rating'] = 900

page = ss['c2l']
user = page['user']
rating = page['rating']
problems = ss.problems
c2 = ss.c2

st.subheader(
    ":grey[ :material/subdirectory_arrow_right: C2 Ladders]", divider='rainbow')


with st.form("c2l_form"):
  users = {ss.users[i]['name']: i for i in ss.users if i != ss.me}
  users = {ss.users[ss.me]['name']+'(me)': ss.me, **users}
  l, r = st.columns(2)
  with l:
    user = st.selectbox(
        "Select User",
        users,
        index=list(users).index(user),
    )
  with r:
    rating = st.number_input(
        'Select Rating',
        min_value=800,
        max_value=3500,
        step=100,
        value=rating,
    )
  user = users[user]
  if st.form_submit_button('Update', type='primary', use_container_width=True):
    st.rerun()

with st.expander('Fillter', icon=':material/filter_list:'):
  no = st.slider('No of Problems', 1, 100, 100)
  od = st.radio('Sort By Frequency', ['Ascending', 'Descending'], index=1)
  shtags = st.toggle('Show Tags')
  tags = c2[str(rating)]['tags'].explode().unique()
  tags = color_tags(tags)
  stags = []
  if shtags:
    stags = st.multiselect('Tags', tags)

if user == ss.me+'(me)':
  user = ss.me

with st.spinner('Processing'):
  data = c2[str(rating)]

  def get_status(row, user):
    if row['id'] in problems.index:
      if row['id'] in ss.users[user]['problems']:
        if ss.users[user]['problems'][row['id']]:
          if row['id'] in ss.users[user]['today']:
            return 'TSolved'
          return 'Solved'
        else:
          return 'Upsolved'
      else:
        return 'Unsolved'
    else:
      return 'Unsolved'
  data['status'] = data.apply(lambda row: get_status(row, user), axis=1)
  if od == 'Ascending':
    data = data.sort_values(by='frequency', ascending=True)
  else:
    data = data.sort_values(by='frequency', ascending=False)
  solved = data[data['status'].str.contains('Solved')]
  todays = data[data['status'].str.contains('TSolved')]
  upsolved = data[data['status'].str.contains('Upsolved')]
  unsolved = data[data['status'].str.contains('Unsolved')]


with st.container(border=True):
  st.subheader(f"User: ***{user}***")
  st.subheader(f"Rating: ***{rating}***")
  o, t = st.columns(2)
  (s, t), (up, un) = o.columns(2), t.columns(2)
  s.metric('Solved', len(solved), len(todays))
  t.metric('Today', len(todays))
  up.metric('Upsolved', len(upsolved))
  un.metric('Unsolved', len(unsolved), -len(upsolved))
  if stags:
    kk = ''.join(
        [f'<span class="round" style="background-color: {tags[tag]}">{tag}</span>' for tag in stags])
    st.subheader(f'Tags:')
    st.html('''<style>
      .round {
      display: inline-block;
      padding: 0.5em 1em;
      border-radius: 1em;
      background-color: #44475a;
      color: white;
      margin: 0.2em;
    }
    </style>'''+kk)

  
punsolved, ptodays, psolved = st.tabs(['Unsolved', 'Today', 'Solved'])
with punsolved:
  us = data[data['status'].str.contains(
      'Upsolved|Unsolved')]
  if stags:
    us = us[us['tags'].apply(lambda x: any(tag in x for tag in stags))]
  us = us.head(no)
  st.markdown(gen_table(us, tags, shtags), unsafe_allow_html=True)
with ptodays:
  if stags:
    todays = todays[todays['tags'].apply(lambda x: any(tag in x for tag in stags))]
  st.markdown(gen_table(todays, tags, shtags), unsafe_allow_html=True)
with psolved:
  if stags:
    solved = solved[solved['tags'].apply(lambda x: any(tag in x for tag in stags))]
  st.markdown(gen_table(solved, tags, shtags), unsafe_allow_html=True)
