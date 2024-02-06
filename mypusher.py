import pusher
import json
from logger import log as log

json_file_path = 'mypusher.json'
with open(json_file_path, 'r') as file:
    pusher_info = json.load(file)


log.debug("pusher key " + pusher_info["key"])

pusher_client = pusher.Pusher(
  app_id=pusher_info["app_id"],
  key=pusher_info["key"],
  secret=pusher_info["secret"],
  cluster='us2',
  ssl=True
)

def notify_shared_users_of_game_change(game_id):
    pusher_client.trigger('lineupgen-shareduser', 'game-changed', {'game_id': game_id})