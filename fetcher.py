#!/usr/bin/env python3
import db
import praw
import time
import json

with open("config.json") as f:
    config = json.load(f)

r = praw.Reddit(client_id=config["id"],
                client_secret=config["secret"],
                user_agent="linux:spez-oversight-committee:2.0.0 (by /u/auxiliary-character)")

r_all = r.subreddit("all")

def ignore_exception_call(f, *args):
    try:
        f(*args)
    except Exception as e:
        print(e)
        print("Error! Skipping.")
        time.sleep(10)

def fetch_post(postid):
    p = r.submission(id = postid)
    db.insert_point(p)
    db.update_post(postid)
    if (time.time() - p.created_utc) > 600 and p.score < 2:
        db.cull_post(postid)

def fetch_new_posts():
    print("Fetching new posts.", time.time())
    for post in r_all.new():
        if not db.get_post(post.id):
            db.insert_post(post)

def fetch_old_posts():
    print("Fetching old posts.", time.time())
    ids = [post["postid"] for post in db.get_active_posts()]
    for postid in ids:
        ignore_exception_call(fetch_post, postid)

def main():
    db.create_db()
    while True:
        ignore_exception_call(fetch_new_posts)
        fetch_old_posts()

if __name__ == "__main__":
    main()
