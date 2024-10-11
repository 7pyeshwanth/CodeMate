from util import *


st.subheader(
    ":grey[ :material/subdirectory_arrow_right: Settings]", divider='rainbow')



st.header('My Profile')
with st.container(border=True):
  card(ss.me)
  if st.button(':material/edit: Edit Profile',
               use_container_width=True):
    updateme()
st.header('Friends')
for friend in ss.users:
  with st.container(border=True):
    if friend == ss.me:
      continue
    card(friend)
    if st.button(':material/delete: Remove', key=friend,
             type='primary', use_container_width=True):
      delfriend(friend)
if st.button(':material/person_add: Add Friend',
            use_container_width=True):
  addfriend()
