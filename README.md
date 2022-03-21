<h1 align="center">
    <b>
        <a href="https://github.com/CraazzzyyFoxx/lavacord.py">
            Lavacord.py
        </a>
    </b>
</h1>


<p align="center">
    <a href="https://discord.gg/J4Dy8dTARf">Support Guild</a> |
    <a href="https://github.com/CraazzzyyFoxx/lavacord.py/tree/main/examples">Examples</a> |
    <a href="https://github.com/CraazzzyyFoxx/lavacord.py">Source</a>
</p>

<br>

Its a lavalink nodes manger to make a music bots for discord with python.


# About

Lavacord.py is a nodes manager to connection with discord voice gateway, easy to create a music bot, you can use to anything async discord wrapper library

# Usage

Example for create connecting with lavalink server using [hikari](https://github.com/hikari-py/hikari).

```python
import hikari
import lavacord

bot = hikari.GatewayBot("token")

lavalink = lavacord.LavalinkClient(bot=bot)


await lavacord.NodePool.create_node(bot, "localhost", 2333, "yourshallpassword")
bot.run()
```

Examples for some methods.
```python
# Auto search mix with track or query
player = await lavalink.create_player(voice_state)
track = await player.search_tracks("Rick Astley", member=member_id)

# Play track
player.queue.put(track)
await player.play(player.queue.get_next_track())

# Pause
await player.pause()

# Resume
await player.resume()

# Volume
await player.volume(volume)

# Previous track
player.queue.get_previous_track()
await player.stop()

# Repeat Mode
player.queue.set_repeat_mode(lavaplayer.RepeatMode.ONE)
```


Examples for some spotify.
```python
import hikari
import lavacord

bot = hikari.GatewayBot("token")

lavalink = lavacord.LavalinkClient(bot=bot)


await lavacord.NodePool.create_node(bot, 
                                    "localhost", 
                                    2333, 
                                    "yourshallpassword",
                                    spotify_client_id="client_id",
                                    spotify_client_secret="client_secret")

player: lavacord.Player = await lavalink.create_player(voice_state, 
                                                       cls=lavacord.Player)
track = await player.search_tracks("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT?si=4ec58d4668b145d2",
                                    member=member_id)
bot.run()
```

# Features

- [x] Spotify support
- [x] connection handler
- [x] Support youtube playlist
- [ ] Add examples

# Installation

```shell
# Linux/OS X
$ pip3 install -U lavaplayer

# Windows
$ pip install -U lavaplayer
```
