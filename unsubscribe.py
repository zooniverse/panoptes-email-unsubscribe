#!/usr/bin/env python

import sys

import psycopg2
import yaml


with open('/database.yml') as db_yaml:
    db_credentials = yaml.load(db_yaml)

prod = db_credentials['staging']

conn = psycopg2.connect(
    host=prod['host'], user=prod['username'], password=prod['password'],
    dbname=prod['database']
)
cur = conn.cursor()

def exec_and_commit(query, *args):
    cur.execute(query, args)
    conn.commit()

def unsub_global(subscribers, slug):
    exec_and_commit(
        ("UPDATE users SET global_email_communication = FALSE "
         "WHERE LOWER(email) = ANY(%s)"),
        subscribers
    )

def unsub_beta(subscribers, slug):
    exec_and_commit(
        ("UPDATE users SET beta_email_communication = FALSE "
         "WHERE LOWER(email) = ANY(%s)"),
        subscribers
    )

def unsub_project(subscribers, slug):
    exec_and_commit(
        ("UPDATE user_project_preferences SET email_communication = FALSE "
         "FROM users, projects "
         "WHERE "
             "user_project_preferences.project_id = projects.id AND "
             "user_project_preferences.user_id = users.id AND "
             "projects.slug ILIKE %s AND "
             "LOWER(users.email) = ANY(%s)"
         ),
        slug,
        subscribers
    )


list_slug = sys.argv[1].lower()

if list_slug.startswith('announcements-') or list_slug == 'announcements':
    unsub_func = unsub_global
elif list_slug == 'beta':
    unsub_func = unsub_beta
else:
    list_slug = '%%/{}'.format(list_slug)
    unsub_func = unsub_project

subscribers = list(map(lambda s: s.strip(), sys.stdin.readlines()))

try:
    if subscribers and list_slug:
        print("Unsubscribing from list {}".format(list_slug))
        unsub_func(subscribers, list_slug)
        print("Unsubscribed {} matching users.".format(cur.rowcount))
finally:
    cur.close()
    conn.close()