# wsrequests

thin wrapper for requests enable websocket.


## how to install

```bash
$ pip install wsrequests
```

## how to use

```python
from wsrequests import WsRequests

wsr = WsRequests()

# login django
# get csrftoken
wsr.get('http://localhost:3000/login')
wsr.post(
    'http://localhost:3000/login',
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

```

