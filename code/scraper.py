import api, config, utilities
from datetime import datetime
import json, time, sys, re

def get_date_string_ymd(timestamp):
  date = datetime.fromtimestamp(float(timestamp))
  return "%04d-%02d-%02d"%(date.year, date.month, date.day)

# awful code, but gets the job done
def get_date_string(timestamp):
  date = datetime.fromtimestamp(float(timestamp))
  datestring_short = "%04d-%02d"%(date.year, date.month)
  datestring_long = "%04d-%02d-%02d"%(date.year, date.month, date.day)
  return (datestring_short, datestring_long)

# makes assumptions about file structure: directory/year-month/year-month-day.json
# also assumes each .json file has a line which might be bad...
# Be warned: if there are no lines in json file, scraper will start from the beginning
def find_newest_timestamp(directory):
  months = sorted(utilities.list_path(directory))
  if months:
    days = sorted(utilities.list_path("%s/%s"%(directory, months[-1])))
    if days:
      last_line = None
      with open("%s/%s/%s"%(directory, months[-1], days[-1])) as f:
        for line in f:
          last_line = line
      # convert the last line to json to find the timestamp
      if last_line:
        message = json.loads(last_line)
        if "ts" in message:
          return message["ts"]
  return time.mktime(datetime.strptime(config.start_date, "%Y-%m-%d").timetuple()) # !@#$!@#%#@

def launch_scrape(directory, method, params, timestamp, umap):
  cur_date = None
  cur_file = None

  user_string = "|".join(umap.keys())

  # CLOSURE
  def replace_uid(match):
    uid = match.group("id")
    if uid in umap:
      return "@%s"%umap[uid]
    return "<@%s>"%uid

  for message in api.message_generator(method, params, timestamp):
    # the format will be line separated json objects for each message because
    # large json objects are the worst

    # update current file
    datestring_short, datestring_long = get_date_string(message["ts"])
    if cur_file is None or cur_date != datestring_long:
      if not cur_file is None:
        cur_file.close()
      cur_date = datestring_long
      utilities.mkdir_p("%s/%s"%(directory, datestring_short))
      cur_file = open("%s/%s/%s.json"%(directory, datestring_short, datestring_long), "a")

    # clean up message object user ids
    if config.replace_user_ids:
      # replace who's talking
      if "user" in message and message["user"] in umap:
        message["user"] = umap[message["user"]]

      # replace mentions (this is a bit slow!)
      if "text" in message:
        message["text"]  = re.sub("<@(?P<id>" + user_string + ")>", replace_uid, message["text"])

    # save! potentially devastating assumption: chronological
    cur_file.write("%s\n"%json.dumps(message))

  if cur_file:
    cur_file.close()

# scrape channels.
def scrape_channels(umap):
  print "Getting channels..."
  for channel in api.channel_generator():
    if not config.scrape_archived_channels and channel["is_archived"]:
      continue
    if not config.scrape_channels_im_not_a_member_of and not channel["is_member"]:
      continue
    directory = "%s/channels/%s/"%(config.directory, channel["name"])
    timestamp = find_newest_timestamp(directory)
    method = "channels.history"
    params = [("channel", channel["id"])]

    sys.stdout.write("Scraping channel \"%s\" starting from %s"%(channel["name"], get_date_string_ymd(timestamp)))
    sys.stdout.flush()
    launch_scrape(directory, method, params, timestamp, umap)
    print ""

# scrape groups. this method is stupidly similar to scrape_channels (decomposition? what's that?)
def scrape_groups(umap):
  print "Getting groups..."
  for group in api.group_generator():
    if not config.scrape_archived_groups and group["is_archived"]:
      continue
    directory = "%s/groups/%s/"%(config.directory, group["name"])
    timestamp = find_newest_timestamp(directory)
    method = "groups.history"
    params = [("channel", group["id"])]

    sys.stdout.write("Scraping group \"%s\" starting from %s"%(group["name"], get_date_string_ymd(timestamp)))
    sys.stdout.flush()
    launch_scrape(directory, method, params, timestamp, umap)
    print ""

# scrape ims. copy paste!!
def scrape_ims(umap):
  print "Getting ims..."
  for im in api.im_generator():
    if not im["user"] in umap:
      continue #wtf
    directory = "%s/ims/%s/"%(config.directory, umap[im["user"]])
    timestamp = find_newest_timestamp(directory)
    method = "im.history"
    params = [("channel", im["id"])]

    sys.stdout.write("Scraping IMs from \"%s\" starting from %s"%(umap[im["user"]], get_date_string_ymd(timestamp)))
    sys.stdout.flush()
    launch_scrape(directory, method, params, timestamp, umap)
    print ""

# HELLO WORLD
if __name__ == "__main__":
  umap = api.user_map()
  if config.scrape_channels:
    scrape_channels(umap)

  if config.scrape_groups:
    scrape_groups(umap)

  if config.scrape_private_messages:
    scrape_ims(umap)