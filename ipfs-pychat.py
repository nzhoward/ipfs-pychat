from threading import Thread
import ipfshttpclient
import base64

listening = True
sending = True
id_set = set()

def listen(client, channel):
    id_self = None
    sub = client.pubsub.subscribe('ping_channel')
    client.pubsub.publish('ping_channel', 'ping')
    for msg in sub:
        id_self = msg['from']
        break
    sub.close()

    print('My ID:', id_self)
    id_set.add(id_self)

    try:
        with client.pubsub.subscribe(channel) as sub:
            if listening:
                for msg in sub:
                    data = base64.b64decode(msg['data']).decode('utf-8')
                    sender = msg['from']
                    if sender not in id_set:
                        print('#### |', sender, 'entered the room')
                        id_set.add(sender)
                    if sender == id_self:
                        print('SENT |', data)
                    else:
                        print('RECV |', data)
            else:
                return
    except Exception as e:
        print(e)
        global sending
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
    exit()
