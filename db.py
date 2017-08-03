#!/usr/bin/env python3
import sqlite3
import time

db = sqlite3.connect("reddit.db")
db.row_factory = sqlite3.Row

def create_db():
    cu = db.cursor()
    cu.executescript("""
    pragma foreign_keys = ON;

    create table if not exists posts (
        postid text primary key not null,
        subreddit text not null,
        title text not null,
        created_utc integer not null,
        last_updated integer not null,
        relevant integer not null
    );

    create table if not exists points (
        id integer primary key autoincrement not null,
        post integer not null,
        timestamp integer not null,
        score integer not null,
        upvote_ratio real not null,
        comments integer not null,
        foreign key(post) references posts(postid)
    );

    create index if not exists points_timestamp_idx on points(timestamp);
    create index if not exists posts_created_utc_idx on posts(created_utc);
    create index if not exists posts_subreddit_idx on posts(subreddit);
    create index if not exists posts_relevant_idx on posts(relevant);
    """)
    db.commit()

def get_post(postid):
    cu = db.cursor()
    cu.execute("select * from posts where postid=?", (postid,))
    return cu.fetchone()

def get_active_posts():
    cu = db.cursor()
    t = int(time.time() - (3600 * 10)) #10 hours ago
    return cu.execute("select * from posts where created_utc>? and relevant=1 order by last_updated limit 100", (t,))

def get_subreddit_posts(subreddit):
    cu = db.cursor()
    return cu.execute("select * from posts where subreddit=?", (subreddit,))

def get_points(postid):
    cu = db.cursor()
    return cu.execute("select * from posts where postid=?", (postid,))

def update_post(postid):
    cu = db.cursor()
    t = int(time.time())
    cu.execute("update posts set last_updated=? where postid=?", (t, postid))
    db.commit()

def cull_post(postid):
    cu = db.cursor()
    cu.execute("update posts set relevant=0 where postid=?", (postid,))

def insert_post(post):
    cu = db.cursor()
    data = {}
    data["id"] = post.id
    data["subreddit"] = post.subreddit.display_name
    data["title"] = post.title
    data["created_utc"] = post.created_utc
    data["last_updated"] = int(time.time())
    data["relevant"] = 1
    cu.execute("insert into posts values (:id,:subreddit,:title,:created_utc,:last_updated,:relevant)", data)
    db.commit()

def insert_point(post):
    cu = db.cursor()
    data = {}
    data["post"] = post.id
    data["timestamp"] = time.time()
    data["score"] = post.score
    data["upvote_ratio"] = post.upvote_ratio
    data["comments"] = post.num_comments
    cu.execute("insert into points values (null, :post, :timestamp, :score, :upvote_ratio, :comments)", data)
    db.commit()

def main():
    create_db()

if __name__ == "__main__":
    main()
