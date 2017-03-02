# panoptes-email-unsubscribe

Basic usage:

```
echo """
    user@example.com
    user2@example.com
    user3@example.com
""" | \
    docker run -i --rm \
        -v /path/to/database.yml:/database.yml \
        zoniverse/panoptes-email-unsubscribe \
        list-name
```
