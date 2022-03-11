from threading import Thread
import ipfshttpclient
import base64
import sys

sending = True
avatar_idx = 0
id_avatar_map = {}
avatars = [u'\U0001F437', u'\U0001F412', u'\U0001F414', u'\U0001F42D', u'\U0001F42F', u'\U0001F431', u'\U0001F43B']


def get_ipfs_id(client):
    # subscribe to dummy channel to get own ipfs ID
    id_self = None
    sub = client.pubsub.subscribe('ping_channel')
    client.pubsub.publish('ping_channel', 'ping')
    for msg in sub:
        id_self = msg['from']
        break
    sub.close()
    return id_self


def listen(client, channel):
    global avatar_idx
    global sending

    # save and display own avatar
    id_self = get_ipfs_id(client)
    id_avatar_map[id_self] = avatars[avatar_idx]
    avatar_idx += 1
    print("I am", id_avatar_map[id_self])

    try:
        with client.pubsub.subscribe(channel) as sub:
            for msg in sub:
                data = base64.b64decode(msg['data']).decode('utf-8')
                id_sender = msg['from']
                if id_sender not in id_avatar_map:
                    id_avatar_map[id_sender] = avatars[avatar_idx]
                    avatar_idx += 1
                    print(id_avatar_map[id_sender], 'entered the room')
                if id_sender == id_self:
                    print(id_avatar_map[id_sender], '|', data)
                else:
                    print(id_avatar_map[id_sender], '|', data)
    except Exception as e:
        print('Connection Closed: Press Enter to Terminate')
        sending = False
        return


def send(client, channel):
    while sending:
        user_input = input()
        if user_input == 'exit()':
            return

        client.pubsub.publish(channel, user_input)


if __name__ == '__main__':
    client = ipfshttpclient.connect()
    channel = 'Chat Room 1'
    print('---' + channel + '---')

    t1 = Thread(target=listen, args=[client, channel], daemon=True)
    t2 = Thread(target=send, args=[client, channel], daemon=True)

    t1.start()
    t2.start()

    t2.join()
    print("---End---")
    sys.exit()