STATE_KEY_MESSAGE_CLIENT    =           "INITIALISATION.CLIENT_PUBLIC_KEY"
#    "content": {
#        "key": ""
#    }
STATE_KEY_MESSAGE_SERVER    =           "INITIALISATION.SERVER_PUBLIC_KEY"
#    "content": {
#        "key": ""
#    }
STATE_AWAIT_TOKEN_CLIENT    =           "INITIALISATION.AWAIT_TOKEN"
#    "content": {}
STATE_KEY_TOKEN_SERVER      =           "INITIALISATION.TOKEN"
#    "content": {
#        "token": ""
#    }
STATE_MESSAGE               =           "MESSAGE"
#    "content": {
#        "security-token": "",
#        "user": "",
#        "message": ""
#    }
STATE_ACK                   =           "ACK"
#    "content": {
#        "security-token": ""
#    }
STATE_NACK                  =           "NACK"
#    "content": {
#        "security-token": ""
#    }
STATE_DISCONNECT            =           "DISCONNECT"
#    "content": {
#        "security-token": ""
#    }
def generate_message_template(state, content):
    return {
        "state": state,
        "content": content
    }