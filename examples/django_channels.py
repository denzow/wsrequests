# coding: utf-8

from wsrequests import WsRequests

wsr = WsRequests()

# login django
wsr.get('http://localhost:3000')
wsr.post(
    'http://localhost:3000',
    data={
        'username': 'your name',
        'password': 'your password',
        'csrfmiddlewaretoken': wsr.cookies['csrftoken'],
        'next': '/',
    }
)

# connect websocket
wsr.connect('ws://localhost:3000/ws/room')
wsr.send_message({'message': 'ping'})
wsr.receive_message()
wsr.disconnect()
