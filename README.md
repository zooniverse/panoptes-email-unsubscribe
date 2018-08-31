# panoptes-email-unsubscribe

Unsubscribes users from Panoptes email lists. Takes input from stdin, one
unsubcription per line, in the format:

```
list-slug email-address
```

Invalid lines are ignored. Unsubscriptions are grouped per list, so it only does
one query per list. Project slugs should not include the username as these
aren't preserved in Mailman; i.e.  "galaxy-zoo", not "zooniverse/galaxy-zoo".
This does mean users will be unsubscribed from projects which happen to have the
same name, but this is an acceptible compromise for now  since the UI for
managing subscriptions in PFE confuses these anyway.

Example usage:

```
echo """
    announcements user@example.com
    beta user2@example.com
    beta user3@example.com
    my-project-slug user3@example.com
""" | \
    docker run -i --rm \
        -v /path/to/database.yml:/database.yml \
        zooniverse/panoptes-email-unsubscribe
```
