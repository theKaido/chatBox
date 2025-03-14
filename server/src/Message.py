STATE_KEY_MESSAGE_CLIENT    =           "INITIALISATION.CLIENT_PUBLIC_KEY"
#    "content": {
#        "key": ""
#    }
STATE_KEY_MESSAGE_SERVER    =           "INITIALISATION.SERVER_PUBLIC_KEY"
#    "content": {
#        "key": "",
#        "token": ""
#    }
STATE_MESSAGE               =           "MESSAGE"
#    "content": {
#        "security-token": "token",
#        "message": "",
#        "room": ""
#    }
STATE_ACK                   =           "ACK"
#    "content": {
#        "status": "ok"
#    }
STATE_NACK                  =           "NACK"
#    "content": {
#        "status": "notok"
#    }

def generate_message_template(state, content):
    return {
        "state": state,
        "content": content
    }