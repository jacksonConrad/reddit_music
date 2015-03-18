import time
import praw
from pprint import pprint
user_agent = ('trancebot')

r = praw.Reddit(user_agent = user_agent)
r.login()
already_done = [];

prawWords = ['things','stuff']
subreddits = ['ElectronicMusic', 'trance', 'DnB']
while True:
    for subreddit in subreddits:
        sr = r.get_subreddit(subreddit)
        for submission in sr.get_hot(limit=10):
            pprint(vars(submission))
            op_text = submission.selftext.lower()
            has_praw = any(string in op_text for string in prawWords)

            if submission.id not in already_done and has_praw:
                # msg = '[PRAW related thread](%s)' % submission.short_link
                # r.send_message('masterjaxx', 'PRAW Thread', msg)
                already_done.append(submission.id)
    time.sleep(1800)
