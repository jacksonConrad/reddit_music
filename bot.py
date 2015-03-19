import time
import praw
import threading
import traceback
import argparse
import sqlite3
import logging
import random
import re
from pprint import pprint


class multithread():
    def __init__(self):
        self.running = True
        self.threads = []

        self.r = praw.Reddit(user_agent = 'MusicCollectorBot')
        self.subreddits = ['trance','electronicmusic']

    def go(self):
        t1 = threading.Thread(target=self.music_stream)
        t2 = threading.Thread(target=self.database_cleaner)
        # Make threads daemonic, i.e. terminate them when main thread
        # terminates. From: http://stackoverflow.com/a/3788243/145400
        t1.daemon = True
        t2.daemon = True
        t1.start()
        t2.start()
        self.threads.append(t1)
        self.threads.append(t2)

    def music_stream(self):
        """ Checks r/trance r/dnb r/electronicmusic for hot jams """
        while True:
            try:
                submission_stream = praw.helpers.submission_stream(self.r, 'trance', limit=None, verbosity=0)
                log.info("Opened submission stream successfully.")
                while self.running == True:
                    submission = next(submission_stream) # get the next submission
                    is_song(submission.title, submission.id)


            except:
                log.info("/r/trance submission stream broke. Retrying in 60.")
                log.debug(traceback.print_exc())
                time.sleep(60)
                pass


    def database_cleaner(self):
        """Cleans up the database, which contains worked-through IDs."""
        while self.running == True:
            now = int(time.time())
            print "now: {}".format(now)

            deleteme = cur.execute("SELECT * FROM songs WHERE d + 86400 < %s" % now)
            i = 0
            if deleteme:
                for i, entry in enumerate(cur.fetchall()):
                    cur.execute("DELETE FROM songs WHERE id = '%s'" % entry[1])
                    i += 0
                i > 0 and log.info("Cleaned %s entries from the database." % i)

            time.sleep(3600)

def join_threads(threads):
    """
    Join threads in interruptable fashion.
    From http://stackoverflow.com/a/9790882/145400
    """
    for t in threads:
        while t.isAlive():
            t.join(5)


### Global methods for accessing database ###
def check(ID):
    check = cur.execute('SELECT submission_id FROM songs WHERE submission_id = "%s" LIMIT 1' % ID)
    for line in check:
        print "We already checked this"
        sleep(10)
        if line:
            return True

# Check if the submission title matches our song regex
# If it does, add it to the database and return True
# Otherwise, return False
def is_song(title, submission_id):
    # Our song object
    song = {
        'artist':'null',
        'name': 'null',
        'year': 'null',
        'url': 'null',
        'subreddit': 'trance',
        'submission_id': submission_id
    }
    # So we can encode unicode characters
    title = u''.join(title).encode('utf-8').strip() 

    # build our regexs
    song_regex = re.compile("([\w|\s]+)-(([\w|\s]+)([\(]([\w|\s]+)[\)])?)", re.IGNORECASE | re.UNICODE)
    year_regex = re.compile("\[(\d+)\]")


    
    try:
        # Check to see if it matches the basic structure:
        # <artist_name> - <song_name> (Optional parentheses)
        m = re.match(song_regex, title)
        if m:
            print "{} MATCH".format(title)
            # Check if OP included a year
            y = year_regex.match(title)
            if y: 
                year = y.group(1).strip()
                song['year'] = year 
            song['artist'] = m.group(1).decode('utf-8').strip()
            song['name'] = m.group(2).decode('utf-8').strip()
            # TODO: Check the URL and make sure it is supported
            print(song)


            add(song) # Add this entry to the database


            # TODO: Check parenthetical stuff for more info

            return True
        else:
            # print "{} NO MATCH".format(title)
            # TODO: log rejected titles into a file
            return False
    except UnicodeEncodeError:
        log.error("Unicode Encode Error for: {}".format(title))
    except UnicodeDecodeError:
        log.error("Unicode Decode Error for: {}".format(title))



def add(song):
    cur.execute('INSERT INTO songs (artist, song, year, subreddit, url, submission_id) VALUES ("%s", "%s", "%s", "%s", "%s", "%s")' % (song['artist'], song['name'], song['year'], song['subreddit'], song['url'], song['submission_id']))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MusicCollectorBot monitors music subreddits for new song posts, adding them to a queue for consumption.')
    parser.add_argument('--verbose', action='store_true', help='Print mainly tracebacks.')
    args = parser.parse_args()

    # SET UP LOGGER
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%X', level=logging.DEBUG if args.verbose else logging.INFO)
    log = logging.getLogger(__name__)
    # log.addFilter(NoParsingFilter())

    # SET UP DATABASE
    db = sqlite3.connect('reddit_music.db', check_same_thread=False, isolation_level=None)
    cur = db.cursor()

    t = multithread()
    # l = linkfix()

    t.go()
    try:
        join_threads(t.threads)
    except KeyboardInterrupt:
        log.info("Stopping process entirely.")
        db.close() # you can't close it enough, seriously.
        log.info("Established connection to database was closed.")
