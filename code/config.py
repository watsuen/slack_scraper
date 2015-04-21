# This is your token for making API calls on behalf of your
# user account! Go here to get your token:
# https://api.slack.com/web
token = ""

# Slack has these user IDs for database purposes. Set this option
# if you want those strings of random numbers replaced with usernames
replace_user_ids = True

# save channels? (True or False)
scrape_channels = True
# save groups? (True or False)
scrape_groups = True
# save private messages (aka IM's)? (True or False)
scrape_private_messages = True


# more fine-grained settings
scrape_archived_channels = False
scrape_channels_im_not_a_member_of = False

scrape_archived_groups = True

# This is where you'd like the data scrape to reside. Default is in
# parent directory
directory = "../data"

# This is the start date of when the scraper will start scraping.
# Defaults to the birth of orca-life!
start_date = "2015-03-01"