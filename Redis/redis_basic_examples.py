import redis

REDIS_CONNECTION = redis.Redis() # Connect a local database.

def get_decoded(r, key):
    encoded = r.get(key)
    return encoded.decode('UTF-8')

def create_user(r, name, username):
    print("Creating user:", username)
    r.hmset('user:' + username, {'name': name, 'username': username})

def subscribe(r, subscriber, creator):
    """A subscriber subscribes to a creator"""
    pipe = r.pipeline() # We use a pipeline to
    pipe.sadd(creator+':subscribers', subscriber)
    pipe.sadd(subscriber+':subscribed', creator)
    pipe.execute()

def get_subscribers(r, username):
    print('Subscribers for:', username)
    for sub in r.smembers(username+':subscribers'):
        print('\t{}'.format(sub))

def list_all_members(r):
    """List each user account's info and any related info."""
    # Loop through all keys
    for k in r.scan(0)[1]:
        # If the key starts with 'user:', loop through all it's keys and print them out.
        if k.decode('utf-8').startswith('user:'):
            username = k.decode('utf-8')[5:]
            print("Info for:", username)
            # Attr
            attr = r.hscan(k, 0)[1]
            for info in attr:
                print('\t{}: {}'.format(info.decode('utf-8'), attr[info].decode('utf-8')))

            # Loop through and print all subscribers
            print("  Subscribers:")
            for subber in r.smembers(username+':subscribers'):
                print("\t{}".format(subber.decode('utf-8')))

            # Loop through and print all channels this account is subscribed to.
            print("  Subscribed to:")
            for subbed in r.smembers(username+':subscribed'):
                print("\t{}".format(subbed.decode('utf-8')))
    print()

create_user(REDIS_CONNECTION, 'Nick', 'najarvis')
create_user(REDIS_CONNECTION, 'Tom', 'tomplaysminecraft')
create_user(REDIS_CONNECTION, 'Roger', 'rman45')
subscribe(REDIS_CONNECTION, 'rman45', 'najarvis')
get_subscribers(REDIS_CONNECTION, 'najarvis')
list_all_members(REDIS_CONNECTION)

REDIS_CONNECTION.hset('nums', 'num', 0)
print(REDIS_CONNECTION.hget('nums', 'num'))
REDIS_CONNECTION.hincrby('nums', 'num')
print(REDIS_CONNECTION.hget('nums', 'num'))
REDIS_CONNECTION.hincrby('nums', 'num2')
print(REDIS_CONNECTION.hget('nums', 'num2'))
