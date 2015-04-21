Hi! Code is under code. System requirements are: python.
Please edit the config.py file under code/config.py before you do
anything else - importantly, you need your slack token to access
anything.

To run the backup program, please run the following under the 
code directory:

	python scraper.py

Data is stored in daily files under each folder. This data is in
line-separated json (one json object per message, one on each line)
format. I didn’t modify whatever fields Slack gives back, so
the data is very ugly. But it’s all there, which is what is counts! :)

I have included the crontab file that I added to my computer’s
cron jobs under code/crontab. This only works on Mac OS; I have no
idea how to schedule jobs on other operating systems! If you have
a mac, open up code/crontab and modify “PATH_HERE” to be the 
precise directory to where slack_scraper is located. Then navigate 
to the “code” directory again and run the following:

	crontab cronjob

That’s it! In theory, the backup job should run at 9PM every day 
if your computer is open!

(please let me know if there are bugs; this is very untested ^^)