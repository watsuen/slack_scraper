import urllib, urllib2, json, random, time, sys
import config

api_url = "https://slack.com/api/"

def setup_check():
  if not config.token:
    print "Please include your user token in config.py!"
    return False

# uses urllib to do make a web request
def web_request(url):
  try_again = 3
  success = False
  while try_again > 0:
    sleep(2) # this is ghetto but ensures that we don't spam the system
    try_again -= 1
    try:
      req = urllib2.Request(url)
      handle = urllib2.urlopen(req)
      if handle.getcode() == 200:
        success = True
        break # we have the data! jump out of the while loop
    except urllib2.HTTPError:
      continue # ???
    except IOError:
      continue
  try:
    if not success:
      return (False, '')
    return (True, handle.read().decode('utf-8'))
  except IncompleteRead:
    return (False, '')

# sleep approximately "seconds" seconds (more or less a poisson process)
def sleep(seconds):
  sleep_time = max(0.25, min(random.expovariate(1.0/seconds), 5))
  time.sleep(sleep_time)

# this is spaghetti code and VERY slack specific
def json_call(method, parameters):
  parameters.append(("token", config.token))
  param_str = "?%s"%urllib.urlencode(parameters) if parameters else ""
  url = "%s%s%s"%(api_url, method, param_str)

  # get stuff and convert to json
  status, contents = web_request(url)
  if status:
    try:
      json_contents = json.loads(contents)
      if 'ok' in json_contents and json_contents['ok']:
        return json_contents
    except ValueError:
      return None
  return None

# a generator specifically for slack messages!!
def message_generator(method, parameters, oldest):
  cur_oldest = oldest
  parameters.append(("inclusive", "0"))
  while True:
    response = json_call(method, parameters + [("oldest", cur_oldest)])
    sys.stdout.write(".") # status dot
    sys.stdout.flush()
    if not "messages" in response or not "has_more" in response:
      break
    # iterate in chronological order
    for message in reversed(response["messages"]):
      yield message # mwahahahaha
    try:
      # only continue if we have lots of messages (in case a convo is going
      # on right now) AND slack tells us there are more messages
      if len(response["messages"]) > 1 and response["has_more"]:
        # the latest timestamp from this batch of messages
        cur_oldest = response["messages"][0]["ts"]
      else:
        break # we done
    except:
      break

# generator for channels
def channel_generator():
  response = json_call("channels.list", [])
  if "channels" in response:
    for channel in response["channels"]:
      yield channel

# generator for direct messages
def im_generator():
  response = json_call("im.list", [])
  if "ims" in response:
    for im in response["ims"]:
      yield im

# generator for users
def user_generator():
  response = json_call("users.list", [])
  if "members" in response:
    for user in response["members"]:
      yield user

# id --> username map
def user_map():
  response = {}
  for user in user_generator():
    response[user["id"]] = user["name"]
  # manually add slackbot because it isn't in the user list...
  response["USLACKBOT"] = "slackbot"
  return response


# generator for users
def group_generator():
  response = json_call("groups.list", [])
  if "groups" in response:
    for group in response["groups"]:
      yield group