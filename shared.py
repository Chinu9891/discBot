isOnline = False


def set_status(status: bool):
    global isOnline
    isOnline = status
    
def get_status():
    return isOnline