#!/usr/bin/env python3
import db
import praw
import time

r = praw.Reddit("Reddit Watch by /u/auxiliary-character v 1.0.0")
r_all = r.get_subreddit("all")

def fetch_new_posts():
    print("Fetching new posts.", time.time())
    for post in r_all.get_new():
        if not db.get_post(post.id):
            db.insert_post(post)

def fetch_old_posts():
    print("Fetching old posts.", time.time())
    ids = [post["postid"] for post in db.get_active_posts()]
    for postid in ids:
        p = r.get_submission(submission_id = postid)
        db.insert_point(p)
        db.update_post(postid)
        if (time.time() - p.created_utc) > 600 and p.score < 2:
            db.cull_post(postid)

def main():
    db.create_db()
    while True:
        fetch_new_posts()
        fetch_old_posts()

if __name__ == "__main__":
    main()
