import json
import os
import random
from asyncio import sleep
import discord
import pafy
import requests
from discord import FFmpegPCMAudio
from discord.ext import commands
from discord.utils import get

global current_songs

tfile = open('token.json')
tfile_data = json.load(tfile)
token = tfile_data['token']

vc = discord.VoiceClient
bot = discord.Client()
client = commands.Bot(command_prefix='$')
current_songs = []
player_cards = []
dealer_cards = []
compliments = ["even if you were cloned, you'd still be one of a kind. and the better looking one.",
               "your smile is proof that the best things in life are free.",
               "if it was legal to marry food, i would still choose you over pizza.",
               "i don't have a favourite colour, it's pretty much whatever you are wearing.",
               "you are like a corner piece of a puzzle. without you, i'm completely lost.",
               "if the last two people on earth were us, i would have no problem repopulating it with you.",
               "if you knew how much i think about you, i would be very embarrassed.",
               "your face makes other people ugly.", "you might be the primary reason for global warming.",
               "are you a beaver, because damn.", "i bet you make babies smile.",
               "you are more unique and wonderful than the smell of a new book.",
               "i'm not drunk, just intoxicated by you.",
               "you are awkward, in a cute way. like an elevator ride, but with puppies.",
               "just like an untrained puppy. i'd really like to take you out.",
               "you make everything better. if people were more like you the world would be perfect."]

insults = ['if laughter is the best medicine, your face must be curing the world.',
           "you're so ugly, you scared the crap out of the toilet",
           "if i had a face like yours, i'd sue my parents.",
           "your birth certificate is an apology letter from the condom factory.",
           "i guess you prove that even god makes mistakes sometimes.",
           "the only way you'll ever get laid is if you crawl up a chicken's ass and wait.",
           "you're so fake, barbie is jealous.", "i’m jealous of people that don’t know you",
           "you're so ugly, when your mom dropped you off at school she got a fine for littering.",
           "you must have been born on a highway because that's where most accidents happen.",
           "i don't know what makes you so stupid, but it really works.",
           "calling you an idiot would be an insult to all the stupid people.",
           "you, sir, are an oxygen thief!", "why don't you go play in traffic.",
           "please shut your mouth when you’re talking to me.", "i'd slap you, but that would be animal abuse.",
           "the last time I saw something like you, I flushed it.", "i can lose weight, but you’ll always be ugly.",
           "why don't you slip into something more comfortable... like a coma."]


class Casino:
    def __init__(self, name, money, wins, debt, losses, reputation):
        self.name = name
        self.money = money
        self.wins = wins
        self.debt = debt
        self.is_gambling = True
        self.reputation = reputation
        self.losses = losses

    def add_win(self):
        self.wins = self.wins + 1
        self.save()
        return self.wins

    def add_loss(self):
        self.losses = self.losses + 1
        self.save()
        return self.losses

    def add_money(self, bet: int):
        self.money = self.money + bet
        self.save()

    def add_debt(self, debt: int):
        if self.money == 0:
            print("You have gone into debt..")
            print("Your debt has gone up")
            self.debt = self.debt + debt
            self.save()
        else:
            print("Your debt has gone up")
            self.debt = self.debt + debt
            self.save()

    def change_name(self, newname):
        self.name = newname
        self.save()

    def indebt(self):
        if self.debt > 0:
            print('You are in debt..')
            print(f'You owe ${self.debt}')
            self.save()
        else:
            print('You are not in debt')
            self.save()

    def addrep(self, rep: int):
        self.reputation = self.reputation + rep
        self.save()

    def remrep(self, rep: int):
        self.reputation = self.reputation - rep
        self.save()

    def save(self):
        playersave = {
            'name': self.name,
            'money': self.money,
            'wins': self.wins,
            'debt': self.debt,
            'losses': self.losses,
            'reputation': self.reputation
        }
        with open(f"{self.name}.json", 'w') as u:
            json.dump(playersave, u)


def get_player(name):
    with open(name + '.json', 'r') as userfile:
        info = json.load(userfile)
        player1 = Casino(
            info['name'],
            info['money'],
            info['wins'],
            info['debt'],
            info['losses'],
            info['reputation'])
    return player1


def q_replace(url):
    if len(current_songs) < 3:
        current_songs.append(url)
        print('adding to the queue')

    else:
        x = len(current_songs) - 1
        current_songs.pop(x)
        current_songs.append(url)
        print('adding to the queue, queue at limit removing last queued up item')


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q']
    return quote


@client.event
async def on_ready():
    print("Logged in as: ", client.user)
    print("--------------------------------")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    global invoker
    invoker = message.author
    inv_server = invoker.guild

    try:
        inv_vchannel = message.author.voice.channel
        print(inv_vchannel)
    except AttributeError:
        print("User is not in a voice channel")

    print(inv_server)
    print("person who last typed: ", invoker)
    print(f"message: {message.content}")
    await client.process_commands(message)


@client.command(pass_context=True, aliases=['j'])
async def join(ctx):
    global voice
    voice = get(client.voice_clients)

    try:
        channel = ctx.message.author.voice.channel
        if channel and voice is None:
            await channel.connect()
        elif voice:
            await ctx.send("I am already in a channel")
        elif channel is None:
            await ctx.send("You need to be in a voice channel")
    except AttributeError:
        await ctx.send("You need to be in a voice channel")
        print("invoker not in channel")


@client.command(pass_context=True, aliases=['dc'])
async def leave(ctx):
    bot_check = get(client.voice_clients)
    if bot_check is None:
        print("No channel to dc from")
    elif bot_check and current_songs != 0:
        current_songs.clear()
        await bot_check.disconnect()
    else:
        await bot_check.disconnect()


@client.command(pass_context=True, aliases=['p'])
async def play(ctx, url: str):

    async def play_next():

        if len(current_songs) != 0:
            bot_player.play(FFmpegPCMAudio(current_songs[0]))
            bot_player.source = discord.PCMVolumeTransformer(bot_player.source)
            bot_player.source.volume = 0.25
            print(f'playing next song')
            current_songs.pop(0)
            while bot_player.is_playing():
                link = pafy.new(url, ydl_opts={'nocheckcertificate': True})
                await sleep(link.length)
                if bot_player.is_playing() is False:
                    break
            await play_next()
        else:
            print('queue is empty')
            return

    try:

        bot_player = ctx.guild.voice_client
        player_status = discord.VoiceClient.is_playing(bot_player)

        if player_status:
            # Here we are checking if our bot is currently playing audio
            link = pafy.new(
                url, ydl_opts={'nocheckcertificate': True}).getbestaudio()
            q_replace(link.url)
            await ctx.send(f'{link.title} was added to the queue')
            print("adding to the queue")
            # If it's playing audio then we only add the url into the queue
        else:
            # If it's not playing audio we want to run the code to play the selected song
            link = pafy.new(
                url, ydl_opts={'nocheckcertificate': True}).getbestaudio()
            q_replace(link.url)
            await ctx.send(f'{link.title} was added to the queue')
            # Creating the url to stream with ffmpeg using pafy
            # It also runs a check to see if the length of the queue is currently maxed out or not

            bot_player = ctx.guild.voice_client
            bot_player.play(FFmpegPCMAudio(current_songs[0]))
            await ctx.send(f'playing {link.title}')
            bot_player.source = discord.PCMVolumeTransformer(bot_player.source)
            bot_player.source.volume = 0.25
            print(f'playing {link.title}')
            current_songs.pop(0)
            # Plays the song

            while bot_player.is_playing:
                link = pafy.new(url, ydl_opts={'nocheckcertificate': True})
                await sleep(link.length)
                if bot_player.is_playing() is False:
                    break
            # This loop checks if the bot is playing audio
            # If the bot is playing audio it will sleep for the duration of the video it's playing

            await play_next()

    except AttributeError:
        # This handles the bot not being in the voice channel
        # It will connect, and then add the song to the queue list and then play it

        await ctx.message.author.voice.channel.connect()
        print('bot not in channel, joining')
        # Bot joins here ^^

        link = pafy.new(
            url, ydl_opts={'nocheckcertificate': True}).getbestaudio()
        q_replace(link.url)
        await ctx.send(f'{link.title} was added to the queue')
        # Creating the url to stream with ffmpeg using pafy
        # It also runs a check to see if the length of the queue is currently maxed out or not

        bot_player = ctx.guild.voice_client
        bot_player.play(FFmpegPCMAudio(current_songs[0]))
        await ctx.send(f'playing {link.title}')
        bot_player.source = discord.PCMVolumeTransformer(bot_player.source)
        bot_player.source.volume = 0.25
        print(f'playing {link.title}')
        # Plays the song

        while bot_player.is_playing:
            link = pafy.new(url, ydl_opts={'nocheckcertificate': True})
            await sleep(link.length)
            if bot_player.is_playing() is False:
                break
        # This loop checks if the bot is playing audio
        # If the bot is playing audio it will sleep for the duration of the video it's playing
        current_songs.pop(0)
        await play_next()
        # Once the audio has finished playing it runs the play_next function
        # This function then just plays through the queue


@client.command(pass_context=True, aliases=['s'])
async def stop(ctx):
    global bot_player
    bot_player = ctx.guild.voice_client
    try:

        status = discord.VoiceClient.is_playing(bot_player)
        print(status)
        discord.VoiceClient.stop(bot_player)
        print(f'bot stopped')
        current_songs.clear()
        print(current_songs)

    except AttributeError:

        print("Not currently playing")


@client.command(pass_context=True, aliases=['next', 'n'])
async def skip(ctx):
    global bot_player
    bot_player = ctx.guild.voice_client
    # Just adding shortcuts to the code

    try:
        # Checking if the bot is currently playing audio
        bot_status = bot_player.is_playing

        if bot_status is False:
            # if the bot is not playing audio we send a message
            await ctx.send("Nothing playing")

        elif bot_status and len(current_songs) != 0:
            # If the bot is playing audio and the queue has at least 1 song in it
            # Then we are going to stop the bot, play the first song in the queue
            await ctx.send("Skipping to next song")
            vc.stop(bot_player)
            current_songs.pop(0)
            bot_player = ctx.guild.voice_client
            bot_player.play(FFmpegPCMAudio(current_songs[0]))
            bot_player.source = discord.PCMVolumeTransformer(bot_player.source)
            bot_player.source.volume = 0.25
            await ctx.send(f'playing next song')
            print(f'playing next song')

        elif bot_status and len(current_songs) == 0:
            print("No songs to skip to in the queue")
            # This one just prints a message if the queue is empty

    except AttributeError:
        await ctx.send("I am not in a voice channel")


@client.command(pass_context=True, aliases=['odds'])
async def roll(ctx):
    diceroll = random.choice(range(1, 6))
    print(diceroll)

    if diceroll == 1:
        await ctx.send(f'[       ]\n'
                       f'[  0  ]\n'
                       f'[       ]\n')

    if diceroll == 2:
        await ctx.send(f'[0    ]\n'
                       f'[       ]\n'
                       f'[    0]\n')

    if diceroll == 3:
        await ctx.send(f'[ 0    ]\n'
                       f'[   0  ]\n'
                       f'[     0]\n')

    if diceroll == 4:
        await ctx.send(f'[ 0   0 ]\n'
                       f'[         ]\n'
                       f'[ 0   0 ]\n')

    if diceroll == 5:
        await ctx.send(f'[ 0   0 ]\n'
                       f'[   0   ]\n'
                       f'[ 0   0 ]\n')

    if diceroll == 6:
        await ctx.send(f'[0   0]\n'
                       f'[0   0]\n'
                       f'[0   0]\n')

    await ctx.send(f'Nice, you rolled a {diceroll}')


@client.command(aliases=['motivate', 'feelgood'])
async def inspire(ctx):
    await ctx.send(get_quote(), tts=True)


@client.command(aliases=['b', 'insult'])
async def bully(ctx, *, target):
    try:
        player1 = get_player(str(ctx.author))
        player1.remrep(1)
        await ctx.send(f'{target}, {random.choice(insults)}')
    except FileNotFoundError:
        await ctx.send(f'{target}, {random.choice(insults)}')


@client.command(aliases=['compliment', 'c'])
async def nice(ctx, *, target):

    try:
        player1 = get_player(str(ctx.author))
        player1.addrep(3)
        await ctx.send(f'{target}, {random.choice(compliments)}')
    except FileNotFoundError:
        await ctx.send(f'{target}, {random.choice(compliments)}')


@client.command()
async def list(ctx):
    print(current_songs)
    print(len(current_songs))


@client.command(aliases=['h', '?', 'commands'])
async def help_me(ctx):
    await ctx.send(f"Hi! I'm Bully Bot\n"
                   f"I was originally designed to bully nrtz\n"
                   f"I can now do lots of other things!\n"
                   f"[COMMANDS]\n"
                   f"$play followed by a youtube link will play that video\n"
                   f"$stop will stop any audio being played\n"
                   f"$skip will skip the current song if there's a queue\n"
                   f"$q followed by a link to create a queue and add the song to it\n"
                   f"$roll to roll a 6-sided die\n"
                   f"$join will bring me to your voice channel\n"
                   f"$leave will disconnect me\n"
                   f"[NOTICE] Most commands can be called by using just their first letter,\n"
                   f"[NOTICE] For example, $play becomes just $p\n"
                   f"[NOTICE] $stop uses $s, $skip does not have a shortened command]\n"
                   f"[NOTICE] I can now play games! I currently play three\n"
                   f"$bet will create your wallet to gamble with\n"
                   f"$blackjack or $21 will start a game of blackjack\n"
                   f"$numbergame or $number will start the number game\n"
                   f"$craps will start a game of craps\n"
                   f"$wallet will display your betting stats\n"
                   f"$pay will allow you to pay your debt if you have one\n"
                   f"$coin will flip a coin\n"
                   f"$refill will allow you to take a loan out")


@client.command(aliases=['bet'])
async def gamble(ctx):
    def add_player(name):
        player1 = Casino(name, 500, 0, 0, 0, 0)
        playersave = {
            'name': name,
            'money': player1.money,
            'wins': player1.wins,
            'debt': player1.debt,
            'losses': player1.losses,
            'reputation': player1.reputation
        }
        with open(f"{name}.json", 'w') as u:
            json.dump(playersave, u)

    gam_name = str(ctx.author)
    if os.path.exists(f'{gam_name}.json'):
        await ctx.send(f'Welcome back, {ctx.author.display_name}')
        player1 = get_player(gam_name)
        await ctx.send(f"You have: ${player1.money}\n"
                       f"Type $blackjack to play blackjack 21\n"
                       f"Type $numbergame to play the number game")
    else:

        await ctx.send(f'No file found, creating you one..')
        add_player(gam_name)
        player1 = get_player(gam_name)
        await ctx.send(f"You have: ${player1.money}\n"
                       f"Type $blackjack to play blackjack 21\n"
                       f"Type $numbergame to play the number game")


@client.command(aliases=['21'])
async def blackjack(ctx):
    cards = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']
    suites = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    deck = []

    def dealercheck():
        if 11 in dealer_cards and sum(dealer_cards) > 21:
            while 11 in dealer_cards and sum(dealer_cards) > 21:
                var = dealer_cards.index(11)
                dealer_cards.pop(var)
                dealer_cards.insert(var, int(1))

    def acecheck():
        if 11 in player_cards and sum(player_cards) > 21:
            while 11 in player_cards and sum(player_cards) > 21:
                var = player_cards.index(11)
                player_cards.pop(var)
                player_cards.insert(var, int(1))

    def convert(pick):

        if 'K' in pick:
            deck.remove(pick)
            return int(10)
        elif 'J' in pick:
            deck.remove(pick)
            return int(10)
        elif 'Q' in pick:
            deck.remove(pick)
            return int(10)
        elif 'A' in pick:
            deck.remove(pick)
            return int(11)
        elif pick[0] in range(2, 11):
            deck.remove(pick)
            return int(pick[0])

    def shuffle():
        deck.clear()
        for x in range(len(cards)):
            for y in range(len(suites)):
                deck.append((cards[x], suites[y]))

    def comparewallet(bet):
        if int(bet) > int(player1.money):
            bet = True
            return bet
        else:
            bet = False
            return bet

    def add_player(name):
        player1 = Casino(name, 500, 0, 0, 0, 0)
        player1.save()

    gam_name = ctx.author
    if os.path.isfile(f"{gam_name}.json"):
        print(f"Welcome back, {gam_name}")
        player1 = get_player(str(gam_name))
    else:
        print('No active file, creating one')
        add_player(str(gam_name))
        player1 = get_player(str(gam_name))

    await ctx.send(f'You have ${player1.money}')
    await ctx.send(f'How much would you like to bet? ')
    check = await client.wait_for('message')
    msg = check.content
    try:
        bet = int(msg)
        betcheck = comparewallet(bet)
        if betcheck:
            await ctx.send('You can only bet what you have')
        else:
            await ctx.send('Bet is good')
            player_cards.clear()
            dealer_cards.clear()
            shuffle()
            player1.is_gambling = True
            while player1.is_gambling:
                while len(player_cards) < 2:
                    pick = random.choice(deck)
                    card = convert(pick)
                    player_cards.append(card)
                while len(dealer_cards) < 2:
                    pick = random.choice(deck)
                    card = convert(pick)
                    dealer_cards.append(card)

                acecheck()
                dealercheck()
                await ctx.send(f'Your cards: {player_cards}, {sum(player_cards)}')
                await ctx.send(f'Dealer is showing {dealer_cards[0]}')

                if sum(dealer_cards) == 21 and sum(player_cards) != 21:
                    await ctx.send('House wins!')
                    await ctx.send(f'You lost ${bet}')
                    if player1.money > 0:
                        player1.remrep(2)
                        player1.add_money(bet * -1)
                        player1.add_loss()
                        player1.is_gambling = False
                    else:
                        player1.remrep(2)
                        player1.add_debt(bet)
                        player1.is_gambling = False
                elif sum(dealer_cards) > 21:
                    await ctx.send("House bust!")
                    player1.add_money(round(bet * 1.3))
                    player1.add_win()
                    await ctx.send(f'You won ${round(bet * 1.3)}, you now have ${player1.money}')
                    player1.is_gambling = False
                elif sum(player_cards) == 21:
                    await ctx.send('Player wins with 21!')
                    player1.reputation = +5
                    player1.add_money(round(bet * 2))
                    player1.add_win()
                    await ctx.send(f'You won ${round(bet * 2)}, you now have ${player1.money}')
                    player1.is_gambling = False
                elif sum(player_cards) > 21:
                    await ctx.send("Player bust!")
                    await ctx.send(f'You lost ${bet}')
                    if player1.money > 0:
                        player1.remrep(2)
                        player1.add_money(bet * -1)
                        player1.add_loss()
                        player1.is_gambling = False
                    else:
                        player1.add_debt(bet)
                        player1.remrep(2)
                        player1.is_gambling = False
                else:

                    hitstay = True
                    while hitstay:
                        await ctx.send('Hit or stay?')
                        action = await client.wait_for('message')
                        if 'hit' in action.content or 'Hit' in action.content:
                            pick = random.choice(deck)
                            card = convert(pick)
                            player_cards.append(card)
                            acecheck()
                            dealer = sum(dealer_cards)
                            player = sum(player_cards)
                            if sum(player_cards) > 21:
                                await ctx.send(f'House wins, player busted!\n'
                                               f'Dealer cards {dealer_cards}, {dealer}\n'
                                               f'Player cards: {player_cards}, {player}')
                                await ctx.send(f'You lost ${bet}')
                                if player1.money > 0:
                                    player1.remrep(2)
                                    player1.add_money(bet * -1)
                                    player1.add_loss()
                                    hitstay = False
                                    player1.is_gambling = False
                                else:
                                    player1.remrep(2)
                                    player1.add_debt(bet)
                                    hitstay = False
                                    player1.is_gambling = False
                            elif sum(player_cards) == 21:
                                await ctx.send(f'Player wins with 21!')
                                player1.reputation = +5
                                player1.add_money(round(bet * 2))
                                player1.add_win()
                                await ctx.send(f'You won ${round(bet * 2)}, you now have ${player1.money}')
                                hitstay = False
                                player1.is_gambling = False
                            elif sum(player_cards) < 21:
                                await ctx.send(f'You have {sum(player_cards)}, {player_cards}')
                            else:
                                await ctx.send('error debug')
                                hitstay = False
                                player1.is_gambling = False

                        elif 'stay' in action.content or 'Stay' in action.content:
                            pulling = True
                            dealer = sum(dealer_cards)
                            while pulling:
                                player = sum(player_cards)
                                if dealer < 17 and dealer < player:
                                    pick = random.choice(deck)
                                    card = convert(pick)
                                    dealer_cards.append(card)
                                    dealercheck()
                                    dealer = sum(dealer_cards)
                                    player = sum(player_cards)
                                    await ctx.send(f"Dealer pulls {dealer_cards[-1]}\n"
                                                   f"Dealer now has {dealer}")
                                    if dealer in range(17, 20) and dealer > player:
                                        await ctx.send(
                                            f"House won! Dealer cards: {dealer_cards}, {dealer}\n"
                                            f"Player cards: {player_cards}, {player}")
                                        await ctx.send(f'You lost ${bet}')
                                        if player1.money > 0:
                                            player1.remrep(2)
                                            player1.add_money(bet * -1)
                                            player1.add_loss()
                                            pulling = False
                                            player1.is_gambling = False
                                            hitstay = False
                                        else:
                                            player1.remrep(2)
                                            player1.add_debt(bet)
                                            pulling = False
                                            player1.is_gambling = False
                                            hitstay = False
                                    elif dealer > 21:
                                        await ctx.send(f'House busted! Dealer cards: {dealer_cards}')
                                        player1.reputation = +5
                                        player1.add_money(round(bet * 1.3))
                                        player1.add_win()
                                        await ctx.send(f'You won ${round(bet * 1.3)}, you now have ${player1.money}')
                                        pulling = False
                                        player1.is_gambling = False
                                        hitstay = False
                                    elif 17 > dealer > player:
                                        await ctx.send(
                                            f'House wins, Dealer cards {dealer_cards}, {dealer}\n'
                                            f'Player cards: {player_cards}, {player}')
                                        await ctx.send(f'You lost ${bet}')
                                        if player1.money > 0:
                                            player1.remrep(2)
                                            player1.add_money(bet * -1)
                                            player1.add_loss()
                                            pulling = False
                                            player1.is_gambling = False
                                            hitstay = False
                                        else:
                                            player1.remrep(2)
                                            player1.add_debt(bet)
                                            pulling = False
                                            player1.is_gambling = False
                                            hitstay = False
                                    elif dealer in range(17, 20) and dealer > player:
                                        await ctx.send(
                                            f"House won! Dealer cards: {dealer_cards}, {dealer}\n"
                                            f"Player cards: {player_cards}, {player}")
                                        await ctx.send(f'You lost ${bet}')
                                        if player1.money > 0:
                                            player1.remrep(2)
                                            player1.add_money(bet * -1)
                                            player1.add_loss()
                                            pulling = False
                                            player1.is_gambling = False
                                            hitstay = False
                                        else:
                                            player1.remrep(2)
                                            player1.add_debt(bet)
                                            pulling = False
                                            player1.is_gambling = False
                                            hitstay = False

                                elif dealer in range(17, 21) and dealer > player:
                                    await ctx.send(f"House won! Dealer cards: {dealer_cards}, {dealer}\n"
                                                   f"Player cards: {player_cards}, {player}")
                                    await ctx.send(f'You lost ${bet}')
                                    if player1.money > 0:
                                        player1.remrep(2)
                                        player1.add_money(bet * -1)
                                        player1.add_loss()
                                        pulling = False
                                        player1.is_gambling = False
                                        hitstay = False
                                    else:
                                        player1.add_debt(bet)
                                        player1.remrep(2)
                                        pulling = False
                                        player1.is_gambling = False
                                        hitstay = False

                                elif player < dealer < 21:
                                    await ctx.send(f'House wins, Dealer cards {dealer_cards}, {dealer}\n'
                                                   f'Player cards: {player_cards}, {player}')
                                    await ctx.send(f'You lost ${bet}')
                                    if player1.money > 0:
                                        player1.remrep(2)
                                        player1.remrep(2)
                                        player1.add_money(bet * -1)
                                        player1.add_loss()
                                        pulling = False
                                        player1.is_gambling = False
                                        hitstay = False
                                    else:
                                        player1.add_debt(bet)
                                        player1.remrep(2)
                                        pulling = False
                                        player1.is_gambling = False
                                        hitstay = False

                                elif dealer == player:
                                    await ctx.send(f'Standoff.. Reshuffling, play again.')
                                    pulling = False
                                    player1.is_gambling = False
                                    hitstay = False

                                elif dealer in range(17, 20) and dealer < player:
                                    await ctx.send(f'Player won!')
                                    player1.add_money(round(bet * 1.3))
                                    player1.add_win()
                                    await ctx.send(f'You won ${round(bet * 1.3)}, you now have ${player1.money}')
                                    pulling = False
                                    player1.is_gambling = False
                                    hitstay = False

                                elif dealer == 21:
                                    await ctx.send(f'House wins, Dealer cards {dealer_cards}, {dealer}\n'
                                                   f'Player cards: {player_cards}, {player}')
                                    await ctx.send(f'You lost ${bet}')
                                    if player1.money > 0:
                                        player1.remrep(2)
                                        player1.remrep(2)
                                        player1.add_money(bet * -1)
                                        player1.add_loss()
                                        pulling = False
                                        player1.is_gambling = False
                                        hitstay = False
                                    else:
                                        player1.add_debt(bet)
                                        player1.remrep(2)
                                        pulling = False
                                        player1.is_gambling = False
                                        hitstay = False

                                else:
                                    await ctx.send('error debug')
                                    print(player_cards)
                                    print(dealer_cards)
                                    pulling = False
                                    player1.is_gambling = False
                                    hitstay = False

    except ValueError:
        await ctx.send("Bet was not a number")


@client.command(aliases=['pay', 'debt'])
async def pay_debt(ctx):
    try:
        player1 = get_player(str(ctx.author))
        if player1.debt > 0:
            await ctx.send(f"Thank you for paying your debt, you owe ${player1.debt}\n"
                           f"How much would you like to pay? You have ${player1.money}")
            check = await client.wait_for('message')
            msg = check.content
            if int(msg) > int(player1.money):
                await ctx.send(f"You don't have that much money..")

            elif int(msg) > int(player1.debt):
                await ctx.send(f"Your debt isn't that high..")

            elif int(msg) == int(player1.debt):
                payoff = int(msg)
                await ctx.send('Your debt is paid off. You gained reputation')
                player1.addrep(5)
                player1.add_money(-payoff)
                player1.add_debt(-payoff)

            else:
                payoff = int(msg)
                player1.add_money(-payoff)
                player1.add_debt(-payoff)
                await ctx.send(f"Your new debt is ${player1.debt}\n"
                               f"You paid ${payoff}")
                player1.save()

    except FileNotFoundError:
        await ctx.send("You don't have a wallet, type $bet to make one.")


@client.command(aliases=['refill'])
async def get_money(ctx):
    try:
        player1 = get_player(str(ctx.author))
        if player1.reputation in range(0, 14):
            await ctx.send(f'Your reputation is only {player1.reputation}, you only get $100\n'
                           f'Your debt has also gone up by $150 (interest), use $pay to pay your debt')
            player1.add_money(100)
            player1.add_debt(150)
            player1.remrep(5)

        elif player1.reputation in range(15, 50):
            await ctx.send(f'Your reputation is {player1.reputation}, you receive $250\n'
                           f'Your debt has only gone up by $100 but you have lost reputation')
            player1.add_money(250)
            player1.add_debt(100)
            player1.remrep(20)

        elif player1.reputation < 0:
            await ctx.send(f'You are one dirty dog... You can have $10 but your debt goes up by $35\n'
                           f'Someone with a reputation of {player1.reputation} is weird')
            player1.add_money(10)
            player1.add_debt(35)
            player1.remrep(5)

        elif player1.reputation > 50:
            await ctx.send("You can have $500 due to your good standing\n"
                           "Your debt only goes up by $300, you lose reputation")
            player1.add_money(500)
            player1.add_debt(300)
            player1.remrep(25)

        elif player1.reputation > 100:
            await ctx.send(f'You are great, $1000 coming your way\n'
                           f'Your debt increases by $500')
            player1.add_money(1000)
            player1.add_debt(500)
            player1.remrep(50)

    except FileNotFoundError:
        await ctx.send("You don't have a wallet, type $bet to make one.")


@client.command()
async def crapshelp(ctx):
    await ctx.send(f"You will roll two dice to start\n"
                   f"If your first roll is a 7 or 11 you win your bet\n"
                   f"If you roll a 2, 3 or 12 you lose\n"
                   f"If you roll a 4, 5, 6, 8, 9, or 10 then that number becomes your point number\n"
                   f"You will then roll until you hit your point number or 7\n"
                   f"If you hit your point number you win, if you hit 7 you lose")


@client.command()
async def craps(ctx):

    crapsnumber = (2, 3, 12)
    winnumber = (7, 11)
    pointnumber = (4, 5, 6, 8, 9, 10)

    async def payout(bet, odds):
        player1 = get_player(str(ctx.author))
        six5 = (6, 8)
        three2 = (5, 9)
        two1 = (4, 10)
        if odds in six5:
            await ctx.send(f"6:5 odds, paying out {round(bet * 1.2)}")
            player1.add_money(int(round(bet * 1.2)))
            player1.add_win()
            player1.addrep(2)
        elif odds in three2:
            await ctx.send(f"3:2 odds, paying out {round(bet * 1.5)}")
            player1.add_money(int(round(bet * 1.5)))
            player1.add_win()
            player1.addrep(4)
        elif odds in two1:
            await ctx.send(f"2:1 odds, paying out {round(bet * 2)}")
            player1.add_money(int(round(bet * 2)))
            player1.add_win()
            player1.addrep(6)

    def comparewallet(bet):
        if int(bet) > int(player1.money):
            bet = True
            return bet
        else:
            bet = False
            return bet

    try:
        player1 = get_player(str(ctx.author))
        player1 = get_player(str(ctx.author))
        await ctx.send(f"Welcome back, {ctx.author.display_name}\n"
                       f"If you need a tutorial type $crapshelp\n"
                       f'You have ${player1.money}\n'
                       f'How much would you like to bet?')
        check = await client.wait_for('message')
        msg = check.content
        try:
            bet = int(msg)
            betcheck = comparewallet(bet)
            if betcheck:
                await ctx.send('You can only bet what you have')
            else:
                await ctx.send('Bet is good\n'
                               'Type roll to roll the dice')
                player1.is_gambling = True
                checkroll = await client.wait_for('message')
                chk = checkroll.content
                while player1.is_gambling:
                    if 'Roll' in chk or 'roll' in chk:
                        die1 = random.randint(1, 6)
                        die2 = random.randint(1, 6)
                        total = int(die1 + die2)
                        await ctx.send(f'You rolled a {total}')
                        if total in crapsnumber:
                            await ctx.send(f"Craps number.. You lose")
                            player1.add_loss()
                            player1.add_money(bet * -1)
                            player1.is_gambling = False

                        elif total in winnumber:
                            await ctx.send(f"Nice! Player wins with a {total}")
                            player1.add_win()
                            player1.add_money(bet)
                            player1.is_gambling = False

                        elif total in pointnumber:
                            point = int(total)
                            await ctx.send(f"Your point number is: {total}\n"
                                           f"Type roll to roll again")
                            checkroll = await client.wait_for('message')
                            chk = checkroll.content

                            if client.user == checkroll.author:
                                return

                            elif 'Roll' in chk or 'roll' in chk:
                                rolling = True
                                while rolling:
                                    die1 = random.choice(range(1, 6))
                                    die2 = random.choice(range(1, 6))
                                    total = die1 + die2
                                    await ctx.send(f'You rolled a {total}')
                                    if total == point:
                                        await ctx.send(f"Nice! You win!")
                                        await payout(bet, point)
                                        player1.is_gambling = False
                                        rolling = False

                                    elif total == 7:
                                        await ctx.send(f"You rolled a 7, you lose")
                                        player1.add_loss()
                                        player1.add_money(bet * -1)
                                        player1.is_gambling = False
                                        rolling = False
                                    else:
                                        await ctx.send(f'Type roll to roll again')
                                        checkroll = await client.wait_for('message')
                                        chk = checkroll.content

        except ValueError:
            await ctx.send('You need to enter a number')

    except FileNotFoundError:
        await ctx.send("You don't have a wallet, type $bet to make one.")


@client.command(aliases=['wallet', 'info'])
async def bet_stats(ctx):

    try:
        player1 = get_player(str(ctx.author))
        await ctx.send(f'Hi, {ctx.author.display_name}\n'
                       f'You have ${player1.money}\n'
                       f'You have {player1.wins} wins\n'
                       f'You have {player1.losses} losses\n'
                       f'Your reputation: {player1.reputation}')
        if player1.debt > 0:
            await ctx.send(f'You are in debt..\n'
                           f'You owe ${player1.debt}')
        else:
            await ctx.send(f'You are not in debt')

    except FileNotFoundError:
        await ctx.send("You don't have a wallet, type $bet to make one.")


@client.command(aliases=['m'])
async def eminem(ctx):
    await ctx.send('Let the Green M&M be a Nasty Little Slut', tts=True)
    await ctx.send(file=discord.File('green.jpg'))


@client.command(aliases=['flip', 'coin'])
async def coin_flip(ctx):
    coin = [1, 2]
    flip = random.choice(coin)
    if flip == 1:
        await ctx.send(f'Heads')
    else:
        await ctx.send('Tails')


@client.command(aliases=['number'])
async def numbergame(ctx):

    def comparewallet(bet):
        if int(bet) > int(player1.money):
            bet = True
            return bet
        else:
            bet = False
            return bet

    await ctx.send("Guess a number 1-12, if you are within 1 number win your bet\n"
                   "If you guess the number you get 3x your bet\n"
                   "You have 2 tries")

    try:
        player1 = get_player(str(ctx.author))
        await ctx.send(f"Welcome back, {ctx.author.display_name}\n"
                       f'You have ${player1.money}\n'
                       f'How much would you like to bet?')
        check = await client.wait_for('message')
        msg = check.content
        try:
            bet = int(msg)
            betcheck = comparewallet(bet)
            if betcheck:
                await ctx.send('You can only bet what you have')
            else:
                await ctx.send('Bet is good')
                tries = 2
                number = random.randint(1, 12)
                player1.is_gambling = True
                while tries != 0:
                    await ctx.send('Which number do you guess 1-12?')
                    checknum = await client.wait_for('message')
                    try:
                        guess = int(checknum.content)
                        if guess > 12 or guess == 0:
                            await ctx.send("You need to pick a number 1-12")
                            return
                        elif guess == number:
                            await ctx.send(f'You got it! The number was {number}')
                            player1.add_money(bet * 3)
                            await ctx.send(f'You won ${bet * 3}, you now have ${player1.money}')
                            player1.add_win()
                            player1.addrep(8)
                            tries = 0
                            player1.is_gambling = False

                        elif guess == number + 1 or guess == number - 1:
                            await ctx.send(f'You were within 1 number, the number is {number}')
                            player1.add_money(bet)
                            player1.add_win()
                            player1.addrep(3)
                            await ctx.send(f'You won ${bet}, you now have ${player1.money}')
                            tries = 0
                            player1.is_gambling = False

                        elif guess != number and guess != number + 1 and guess != number - 1:
                            tries = tries - 1
                            await ctx.send(f'Not the correct number..')

                            if tries == 1:
                                await ctx.send(f'Last try')

                            elif tries == 0:
                                await ctx.send(f'The number was {number}, you lost ${bet}')
                                if player1.money > 0:
                                    player1.remrep(2)
                                    player1.add_money(bet * -1)
                                    player1.add_loss()
                                    player1.is_gambling = False
                                else:
                                    player1.add_debt(bet)
                                    player1.is_gambling = False
                    except ValueError:
                        print('you can only type a number 1-12')
        except ValueError:
            await ctx.send("Bet was not a number")

    except FileNotFoundError:
        await ctx.send("You don't have a wallet, type $bet to make one.")


client.run(token)
