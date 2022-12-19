# Twitch Chatbot using Python Asyncio

The aim of this project is to provide an extendable, high performing and low impact chatbot for Twitch chat.

For more information on Twitch and chatbots running on it [follow this link](https://dev.twitch.tv/docs/irc).


## Architecture

Python's Asyncio library is useful especially in cases where much time is spent waiting on IO. In the case of a chatbot
a lot of the time will be spent simply waiting on a socket to the Twitch server for data. In a similar way any 
integration 
triggered by the chatbot will likely also be waiting on some remote endpoint to provide feedback.

What this chatbot is not meant to do is any sort of CPU intensive work. This would include processing data such as 
large text, images or sound to name a few things that can consume many cycles. Worth also pointing out any handler that 
is meant to work with this Chatbot should not be using sleep (in a real use case) which will cause any task to 
potentially slow throughput. The bot simply acts as an intermediary between Twitch and various other services. 
Rather than work as a monolithic application we expect to be useful in a service based architecture where 
these services can do much of the heavy lifting, and be built to purpose.

All that out of the way now a quick overview of what we are working with. Asyncio contains the low level [Transport 
and Protocol](https://docs.python.org/3.8/library/asyncio-protocol.html) which are useful to abstract out Twitch's 
chatbot protocol. These 
constructs are in contrast to the high 
level [Streams](https://docs.python.org/3.8/library/asyncio-stream.html#tcp-echo-client-using-streams) which 
facilitate a much simpler, direct way to do socket io when working with Asynchio. For our needs well want to use 
transports and protocols. These allow creating a high performing callback based implementation of this chatbot 
protocol. Underlying needs such as establishing socket connection to server, authenticating, channel and user info, and 
handling keep alive messages from the server can all be abstracted away. Any non-core events coming from the server 
(mainly text messages from chat users) will be parsed into lightweight objects that are passed along to an event bus.
These objects will contain the basic metadata included in a payload from the chat server.

To pass information from the protocol layer to the event processing layer we use Asyncio [Queues](https://docs.python.org/3/library/asyncio-queue.html)
which allow for feeding the events out across any number of Asyncio [Tasks](https://docs.python.org/3.8/library/asyncio-task.html).
In this way we can also easily configure a pool of Tasks that will allow scaling our bot as required.

A todo in the future will be to add rate limiting into the design. This is a primary function and should live 
under the Asyncio Protocol we are building for twitch chat. The event processing layer should not need to be aware 
of any abuses at the chat level.

## Applications

Simple:
* Create and manage chat baubles such as polls, music/video playlist, product wishlists
* Quick search/lookups for things like wikipedia, youtube and general web search

More complex:
* Twitch <--> Discord bridging... post Twitch messages into discord, get info on Discord
* Game api integration... Dota2 get player stats