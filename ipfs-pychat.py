from threading import Thread
import ipfshttpclient
import base64

listening = True
sending = True


def listen(client, channel):
    try:
        with client.pubsub.subscribe(channel) as sub:
            if listening:
                for msg in sub:
                    data = msg['data']
                    sender = msg['from']
                    print('FROM', sender)
                    print(base64.b64decode(data).decode('utf-8'))
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
