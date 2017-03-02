#!/usr/bin/env python

import os
import sys

import psycopg2
import yaml


with open('/database.yml') as db_yaml:
    db_credentials = yaml.load(db_yaml)


db = db_credentials[os.environ.get('PANOPTES_ENV', 'production')]

conn = psycopg2.connect(
    host=db['host'],
    user=db['username'],
    password=db['password'],
    dbname=db['database'],
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

input_lines = map(lambda s: s.strip(), sys.stdin.readlines())

unsubscriptions = {}

for input_line in input_lines:
    try:
        list_slug, subscriber = input_line.split(" ")
    except ValueError:
        continue
    unsubscriptions.setdefault(list_slug, set()).add(subscriber)

try:
    for list_slug, subscribers in unsubscriptions.items():
        subscribers = list(subscribers)
        if (
            list_slug.startswith('announcements-')
            or list_slug == 'announcements'
        ):
            unsub_func = unsub_global
        elif list_slug == 'beta':
            unsub_func = unsub_beta
        else:
            list_slug = '%%/{}'.format(list_slug)
            unsub_func = unsub_project

        if subscribers and list_slug:
            print("Unsubscribing from list {}".format(list_slug))
            unsub_func(subscribers, list_slug)
            print("\tUnsubscribed {} of {} matching users.".format(
                cur.rowcount,
                len(subscribers),
            ))
finally:
    cur.close()
    conn.close()
