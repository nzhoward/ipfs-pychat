from threading import Thread
import ipfshttpclient
import base64

listening = True
sending = True
id_set = {}
avatars = [u'\U0001F437', u'\U0001F412', u'\U0001F414', u'\U0001F42D', u'\U0001F42F', u'\U0001F431', u'\U0001F43B']
avatar_idx = 0

def listen(client, channel):
    global avatar_idx
    global sending

    # subscribe to dummy channel to get own ipfs ID
    id_self = None
    sub = client.pubsub.subscribe('ping_channel')
    client.pubsub.publish('ping_channel', 'ping')
    for msg in sub:
        id_self = msg['from']
        break
    sub.close()

    id_set[id_self] = avatars[avatar_idx]
    avatar_idx += 1
    print("I am", id_set[id_self])

    try:
        with client.pubsub.subscribe(channel) as sub:
            if listening:
                for msg in sub:
                    data = base64.b64decode(msg['data']).decode('utf-8')
                    id_sender = msg['from']
                    if id_sender not in id_set:
                        id_set[id_sender] = avatars[avatar_idx]
                        avatar_idx += 1
                        print('# | ', id_set[id_sender], 'entered the room')
                    if id_sender == id_self:
                        print(id_set[id_sender], '|', data)
                    else:
                        print(id_set[id_sender], '|', data)
            else:
                return
    except Exception as e:
        print(e)
        sending = False
        return


def send(client, channel):
    while sending:
        user_input = input()
        if user_input == 'exit()':
            global listening
            listening = False
            return

        client.pubsub.publish(channel, user_input)


if __name__ == '__main__':
    client = ipfshttpclient.connect()
    channel = 'Chat Room 1'
    print('---' + channel + '---')

    t1 = Thread(target=listen, args=[client, channel])
    t2 = Thread(target=send, args=[client, channel])

    t1.start()
    t2.start()

    t2.join()
    print("---End---")
