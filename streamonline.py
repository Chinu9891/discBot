from twitchAPI.twitch import Twitch
from twitchAPI.helper import first
import asyncio
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.object.eventsub import StreamOfflineEvent
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.type import AuthScope
APP_ID = 'u2cq9ftafxltwt1qm45l42j5xnrepy'
APP_SECRET = 'huaxi334snizya9e2yes3z70q5ad3g'


from twitchAPI.twitch import Twitch
from twitchAPI.helper import first
import asyncio

async def on_event(data: StreamOfflineEvent):
    print('TESTING PLS')

async def twitch_example():
    # initialize the twitch instance, this will by default also create a app authentication for you
    USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
    twitch = await Twitch(APP_ID, APP_SECRET)
    helper = UserAuthenticationStorageHelper(twitch, USER_SCOPE)
    await helper.bind()
    # call the API for the data of your twitch user
    # this returns a async generator that can be used to iterate over all results
    # but we are just interested in the first result
    # using the first helper makes this easy.
    user = await first(twitch.get_users(logins='chinuuuuuuu'))
    # print the ID of your user or do whatever else you want with it
    print(user.id)
    eventsub = EventSubWebsocket(twitch)
    eventsub.start()
    await eventsub.listen_stream_offline(user.id,on_event)
    inpt = input('Enter yes')
    if inpt == 'yes':
        await eventsub.stop()
        await twitch.close()
# run this example
asyncio.run(twitch_example())