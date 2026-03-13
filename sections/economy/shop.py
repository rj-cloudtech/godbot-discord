import discord
from discord.ext import commands
from discord import app_commands
import random
import settings
import json
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data.json")

# Example GIFs and messages (replace with actual imports from shop_gif.py and shop_xp.py)
GIFS = {
    "slap": [
        "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExaGVicnd5ZDk4Z3hnamJqdjhpZmxjOWdsZnhrczU5aTJ4MjN0c3VxOSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/h8Tdp85UxcATpzaKeL/giphy.gif",
        "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExNTd6cjg5cjUzbmxybGVrdnI0YXE3YzFhYWJnbzU4NW11a2JvMWZveSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/VIQ44kXvLUSQ4PevGU/giphy.gif",
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2UyM25ja2hobDlneTI5c2t0dnBvNmw2dmxlYnlyeXZxajRra241eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/vxvNnIYFcYqEE/giphy.gif",
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExenp1d2FuMG5xcnFhZmU0enQzc2xtaGhlMHUydGQ2aTFkbHVhc2U2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mEtSQlxqBtWWA/giphy.gif",
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExemQwbHVscjVvMzlnNmFtcHl3M3d4YWgxeTJsN2dnd2JtYmxtY3c4byZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/uG3lKkAuh53wc/giphy.gif",
        "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExdTNlYzlpeDZvMXNuNDBicnJlZ3pobzQ5bTR0cWo3MmU2NHcwejZhOSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9UrTPTEbTOQlq/giphy.gif",
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExMWp0aTBoNGF6Zmw5Y2RmOGcxcWIxYWFsejFnbjJ6dTl0c2Z5NWR4dyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3XlEk2RxPS1m8/giphy.gif",
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExemtqdG4wNjlpM3BhZDVhcmh5M3d6a3lvamM0emFvbWQ3aHNuaWZ5ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1v6NLTj3ND6Ss/giphy.gif",
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExMGY3eHplczVyZTlsdGFxdjcwaG52d25hYjFyb2VreXJhMWg1ZWFzdiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Qvwc79OfQOa4g/giphy.gif",
        "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExazcwOHplaHU3d3Ruc3NwYmRhY2lrZHF2ZjZjc3Z1Ymd0dGhmMmVtNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/60rUVyj8ShyuEhHbaz/giphy.gif",
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExbWdrYWp5Njg1ZGJ0dGozMGM3MGZmcnUxaDBrMHVrbzdob3M2eTNlNSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mJWDiMyXuWG8U/giphy.gif",
        "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExa3VsZmpxb3VjcXFnbGx2ZXZrNmJkZmtlMnV1ODNwcHd1dDFpN2RleCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/LSc9OoFCKcVlLYYb3d/giphy.gif"
    ],
    "kick": [
        "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExaTlndGU1ZzUxaTB0aXI0cnBhcHl0cDBkb2RrMGdlY2pqbTd5MWY3eiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l3V0j3ytFyGHqiV7W/giphy.gif",
        "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjhmZGFvaDYyMnVodDR4eHNkYWY5N2JobXFxMTN4MzJ5djVkcGF2YiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l1J3AS8RShMebsmgU/giphy.gif",      
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExdWg1d2g2OWdjZmJsNGl6b3A5MjY5eWxpYWUzM2o0M2kxZDRlbnVkbCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/wngaqQaMycRos/giphy.gif",
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDUzaGt2MGM3OWY2ZDZtdW85NTFrYzRsNmgyOXlwZWNoMjQ2Z20ydCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0qq7t4s8SRJeLkidIm/giphy.gif",
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTB3aWppeGtzYmloNTlqdXR6bWhpa2k5c2o4OG1qb282dDJyd3ZhZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7TKwVQMoQh2At9qU/giphy.gif",
        "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExZzAzb3hiOGhybDR3ZTIyNWJmZ3pxODRtM3dzNmNrNHd0OGkzNDRyNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cmHIuUripuRrpzutQt/giphy.gif",
        "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZmZmNjJ1cmN1bm5qbGJheWp2Mno1ZnhyYm41NGQ4OXR0eXJrOWdjcyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5jQ2FIhtc3M88/giphygif",
        "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExa3JsZmQxaTZ3OWYyaDZ2NjVnY3B0b3huNGU5bTQ4cWt0YTFmeWd2YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/qiiimDJtLj4XK/giphy.gif"
    ],
    "poke": [
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExamw4N3hsbnl3ZWJrazFiZ2x1ZzE1cWc5ZXJwemNnMHJuamExY2o2dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/PkR8gPgc2mDlrMSgtu/giphy.gif",
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExeTQ2aGt5OGNrMzNsOGZzbGFiMG1xcnIyd3BkOHMyYTUwN2xmMzNlbyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1gQwMNJ9z1mqABgQd3/giphy.gif",
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExY2VvaGpuMWxkYmtxMHR1NWY2aXUyendrNndoMzd0c3pnb3M3bzNxbSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jCENc3aA4fLJm/giphy.gif",
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExejFna3ZraHlyMjY2bzA2aDcwYjAyeHpyMWhiYTQ1M2Z6OXZqd2VhcCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/iJ6cUJ4a2yyMljPFIA/giphy.gif",
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExbjNrMTVhOHh0czc1b3JwZzlxM3ZiMXIwamlpNGV0NmVyYmR4N2dkNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oEjI49ChsFQwX7VBK/giphy.gif",
        "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbHFwdzFxbjYzbWJobTlzaTc3cnI1bDRyMWM4c3Z2YWV2Z2FpankyNiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/wzvZLpnCeqN2M/giphy.gif",
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExMml5ZTVlYWRxaHptcjRyYmJqbHBoZGh4YmVydzIweHRqZXo1aWVlNSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/wsUuwZ0pdhUMxvO55c/giphy.gif",
        "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExazFtZTk2Z3NkN2NnOXp5NGRpZnJ5YzhiNGVybXlxM3VlOWZwZjliNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/VfRWPyGjuuagqAkzI1/giphy.gif"
    ],
    "hug": [
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExd3lmaTJkZ2dzOThyN202bW9pNXh2czY5bXlrNmEwb3g3aGV4bGVrZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/VbawWIGNtKYwOFXF7U/giphy.gif",
        "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWl0dHV2dTUzMGp1OXJ3cXJqeTd4dGF6dmRibjgxY2QyaGhwbTlrYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/hpqEHkxVzv8q26xKeC/giphy.gif",
        "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGRmdzRsZjFsbGc5NG9xeGN0Y3plbGpsZHA3Mmpja3Q1Zmk0M2RrYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/TIG6XFVuOriidsTsdu/giphy.gif",
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExc2V4MHMxdTVoazQ4YjF5eWh2ajZtN2o1ZXhzMW81MG13NHQ4ZGMzcCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/hRCFBt3ta0DJeGto2R/giphy.gif",
        "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExMWgxaHZ1M3JudHU5YmJiZHk0YzJvamd0azg5NTBscmxjeHF2MHZsYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/VduFvPwm3gfGO8duNN/giphy.gif",
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExNG10YXNsYzQxdWx3ZmE5YjJqbWJpaWJlbmxrNHh1YnRsYnR2dXZldiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/yidUzriaAGJbsxt58k/giphy.gif",
        "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdXBod2lxeXNsemdlZml0aW50bmlvZjdjbXZicXd1M2pra211cW5sdiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/42YlR8u9gV5Cw/giphy.gif",
        "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXV1aWZweXVpajM0MmpyYjloN3A1ZjBsaWc3MGQyZDRxcmpyd3V1aSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/4No2q4ROPXO7T6NWhS/giphy.gif",
        "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExemV4bHBqMTE2MXIzNnFkb2k1dG9kZmFpcnJkdmszYnV4emgwZ3gycSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/KL7xA3fLx7bna/giphy.gif",
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExbWw2dGsxODMwOXptcG1rOHMwc25lZ2hhbHoxbHljMzZ6ZTVlYWNmdiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l3V0Akmv7LTfIHK6c/giphy.gif",
        "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExeWw0azFvdGZvdndxZ24zaTZsdWtkcTB0YXhhMGYxOWR1MjdtbjR4dyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/llmZp6fCVb4ju/giphy.gif"
    ],
    # ...add other categories as needed...
}

CATEGORY_MESSAGES = {
    "slap": [
        "{sender} just gave {receiver} a slap they won't forget!",
        "Ouch! {receiver} just got slapped by {sender}!",
        "{sender} delivers a world-class slap to {receiver}!",
        "{receiver}, you just got a slap from {sender}!",
        "{sender} and {receiver} are having a slap battle!",
        "{sender} slaps {receiver} so hard, even the internet felt it!",
        "{receiver} is seeing stars after that slap from {sender}!",
        "{sender} just upgraded {receiver}'s face with a handprint!",
        "{sender} says: 'Tag, you're it!' *slap*",
        "{receiver} just got a surprise slap from {sender}!",
        "{sender} slaps {receiver} with the force of a thousand memes!",
        "{receiver} now knows the true meaning of slapstick, thanks to {sender}!",
        "{sender} just gave {receiver} a five-finger salute!",
        "{sender} slaps {receiver} and the echo is still ringing!",
        "{receiver} got a slap so epic, it deserves its own gif!",
    ],
    "kick": [
        "{sender} kicked {receiver} right into next week!",
        "That was a powerful kick from {sender} to {receiver}!",
        "{receiver} just got kicked by {sender}!",
        "{sender} shows off their kicking skills on {receiver}!",
        "{sender} and {receiver} are having a kicking contest!",
        "{sender} kicks {receiver} so hard, their shoes flew off!",
        "{receiver} just got a boot to the feels from {sender}!",
        "{sender} delivers a roundhouse kick to {receiver}!",
        "{sender} says: 'This is Sparta!' and kicks {receiver}!",
        "{receiver} is airborne after that kick from {sender}!",
        "{sender} kicks {receiver} into the next Discord server!",
        "{receiver} just got a flying kick from {sender}!",
        "{sender} kicks {receiver} and the crowd goes wild!",
        "{sender} just gave {receiver} a reality check... with their foot!",
        "{receiver} is now a certified football after that kick from {sender}!",
    ],
    "hug": [
        "{sender} gives {receiver} a warm hug!",
        "{receiver} just got hugged by {sender}!",
        "{sender} and {receiver} share a wholesome hug!",
        "{sender} wraps {receiver} in a big hug!",
        "So much love! {sender} hugs {receiver} tightly!",
        "{sender} gives {receiver} a bear hug!",
        "{receiver} is now 100% more loved thanks to {sender}'s hug!",
        "{sender} hugs {receiver} and won't let go!",
        "{sender} and {receiver} are now in a hug loop!",
        "{receiver} just got a surprise hug from {sender}!",
        "{sender} hugs {receiver} so tight, the internet feels it!",
        "{sender} and {receiver} just broke the hug record!",
        "{sender} gives {receiver} a hug that lasts forever!",
        "{receiver} is now a certified hugger thanks to {sender}!",
        "{sender} hugs {receiver} and the world is a better place!",
    ],
    # ...add other categories as needed...
}

XP_MESSAGES = [
    "{member.mention} just got {amount} XP! Don't spend them all in one place... actually, you can't spend them at all.",
    "{amount} XP for {member.mention}! They're like socks at Christmas: you can't give them away.",
    "{member.mention}, you just got {amount} XP! They're yours forever. No refunds.",
    "Congrats {member.mention}, {amount} XP! They're non-transferable, just like your sense of humor.",
    "{member.mention} received {amount} XP! You can't spend them, but you can brag about them.",
    "{amount} XP for {member.mention}! Use them wisely... oh wait, you can't use them at all.",
    "{member.mention}, {amount} XP! They're more loyal than your last pet rock.",
    "{amount} XP for {member.mention}! They're like your childhood trophies: you can't give them away.",
    "{member.mention} just got {amount} XP! They're stuck with you, like glitter after a craft project.",
    "{amount} XP for {member.mention}! You can't spend them, but you can stare at them lovingly.",
    "{member.mention}, {amount} XP! They're as permanent as your internet history.",
    "{amount} XP for {member.mention}! They're yours to keep, like that embarrassing username.",
    "{member.mention} just got {amount} XP! They're not for sale, trade, or barter.",
    "{amount} XP for {member.mention}! They're like your favorite meme: you can't let them go.",
    "{member.mention}, {amount} XP! They're more attached to you than your phone.",
    "{amount} XP for {member.mention}! You can't spend them, but you can tell your friends you have them.",
    "{member.mention} just got {amount} XP! They're as unspendable as Monopoly money.",
    "{amount} XP for {member.mention}! They're yours, whether you want them or not.",
    "{member.mention}, {amount} XP! They're like your shadow: always with you.",
    "{amount} XP for {member.mention}! You can't give them away, but you can cherish them.",
    "{member.mention} just got {amount} XP! They're more clingy than your ex.",
    "{amount} XP for {member.mention}! They're yours for life. No exchanges.",
    "{member.mention}, {amount} XP! They're as non-refundable as a bad haircut.",
    "{amount} XP for {member.mention}! You can't spend them, but you can flex them.",
    "{member.mention} just got {amount} XP! They're like a tattoo: permanent and questionable.",
    "{amount} XP for {member.mention}! They're yours, like it or not.",
    "{member.mention}, {amount} XP! They're more loyal than your WiFi connection.",
    "{amount} XP for {member.mention}! You can't spend them, but you can screenshot this message.",
    "{member.mention} just got {amount} XP! They're as unspendable as your New Year's resolutions.",
    "{amount} XP for {member.mention}! They're yours, and only yours.",
    "{member.mention}, {amount} XP! They're more permanent than your last online status.",
    "{amount} XP for {member.mention}! You can't give them away, but you can name them.",
    "{member.mention} just got {amount} XP! They're as non-transferable as your DNA.",
    "{amount} XP for {member.mention}! They're yours, like that one sock you can't find the pair for.",
    "{member.mention}, {amount} XP! They're more attached than your favorite hoodie.",
    "{amount} XP for {member.mention}! You can't spend them, but you can count them every night.",
    "{member.mention} just got {amount} XP! They're as unspendable as your browser bookmarks.",
    "{amount} XP for {member.mention}! They're yours, and they're not going anywhere.",
    "{member.mention}, {amount} XP! They're more permanent than your last typo.",
    "{amount} XP for {member.mention}! You can't give them away, but you can show them off.",
    "{member.mention} just got {amount} XP! They're as non-refundable as your last online purchase.",
    "{amount} XP for {member.mention}! They're yours, like your favorite playlist.",
    "{member.mention}, {amount} XP! They're more loyal than your alarm clock.",
    "{amount} XP for {member.mention}! You can't spend them, but you can dream about it.",
    "{member.mention} just got {amount} XP! They're as unspendable as your old game saves.",
    "{amount} XP for {member.mention}! They're yours, and they're here to stay.",
    "{member.mention}, {amount} XP! You can't give them away, but you can write a song about them.",
    "{amount} XP for {member.mention}! They're as non-transferable as your favorite mug.",
    "{member.mention} just got {amount} XP! They're yours, like your secret snack stash.",
    "{member.mention}, {amount} XP! They're more loyal than your favorite pen.",
    "{amount} XP for {member.mention}! You can't spend them, but you can tell your grandkids.",
    "{member.mention} just got {amount} XP! They're as unspendable as your old homework.",
    "{amount} XP for {member.mention}! They're yours, and they're not going anywhere.",
    "{member.mention}, {amount} XP! They're more permanent than your last online rant.",
    "{amount} XP for {member.mention}! You can't give them away, but you can write a poem about them.",
    "{member.mention} just got {amount} XP! They're as non-refundable as your last impulse buy.",
    "{amount} XP for {member.mention}! They're yours, like your favorite meme.",
    "{member.mention}, {amount} XP! They're more loyal than your favorite chair.",
    "{amount} XP for {member.mention}! You can't spend them, but you can frame this message.",
    "{member.mention} just got {amount} XP! They're as unspendable as your old passwords.",
    "{amount} XP for {member.mention}! They're yours, and they're here to stay.",
    "{member.mention}, {amount} XP! They're more permanent than your last playlist.",
    "{amount} XP for {member.mention}! You can't give them away, but you can write a story about them.",
    "{member.mention} just got {amount} XP! They're as non-transferable as your favorite pillow.",
    "{amount} XP for {member.mention}! They're yours, like your favorite snack.",
    "{member.mention}, {amount} XP! They're more loyal than your favorite shoes.",
    "{amount} XP for {member.mention}! You can't spend them, but you can tell your pet.",
    "{member.mention} just got {amount} XP! They're as unspendable as your old phone.",
    "{amount} XP for {member.mention}! They're yours, and they're not going anywhere.",
    "{member.mention}, {amount} XP! They're more permanent than your last online crush.",
    "{amount} XP for {member.mention}! You can't give them away, but you can write a haiku about them.",
    "{member.mention} just got {amount} XP! They're as non-refundable as your last pizza order.",
    "{amount} XP for {member.mention}! They're yours, like your favorite hoodie.",
    "{member.mention}, {amount} XP! They're more loyal than your favorite blanket.",
    "{amount} XP for {member.mention}! You can't spend them, but you can tell your neighbor.",
    "{member.mention} just got {amount} XP! They're as unspendable as your old laptop.",
    "{amount} XP for {member.mention}! They're yours, and they're here to stay.",
]

SHOP_ITEMS = [
    # Fish equipment
    {"id": 101, "name": "Fishing Rod", "price": 10, "category": "Fish equipment"},
    {"id": 102, "name": "Lucky Rabbit's Foot", "price": 100, "category": "Fish equipment"},
    {"id": 103, "name": "Fishing Boat", "price": 1000, "category": "Fish equipment"},
    # Archeology equipment
    {"id": 201, "name": "Indiana Jones's Map", "price": 2000, "category": "Archeology equipment"},
    {"id": 202, "name": "Indiana Jones's Whip", "price": 2000, "category": "Archeology equipment"},
    {"id": 203, "name": "Indiana Jones's Shovel", "price": 2000, "category": "Archeology equipment"},
    {"id": 204, "name": "Indiana Jones's Brush", "price": 2000, "category": "Archeology equipment"},
    # Gold mine equipment
    {"id": 301, "name": "Bulldozers", "price": 1, "category": "Gold mine equipment"},
    {"id": 302, "name": "Excavators", "price": 1, "category": "Gold mine equipment"},
    {"id": 303, "name": "Dump Trucks", "price": 1, "category": "Gold mine equipment"},
    {"id": 304, "name": "Wash Plant", "price": 1, "category": "Gold mine equipment"},
    {"id": 305, "name": "Trommel", "price": 1, "category": "Gold mine equipment"},
    {"id": 306, "name": "Generators & Pumps", "price": 1, "category": "Gold mine equipment"},
    {"id": 307, "name": "Gold Tables & Sluices", "price": 1, "category": "Gold mine equipment"},
    # Badges (roles)
    {"id": 401, "name": "Deagle Dominator", "price": 1000, "category": "Badges", "role_id": 1349738104478498888},
    {"id": 402, "name": "AWPortunitist", "price": 1000, "category": "Badges", "role_id": 1349803122477895862},
    {"id": 403, "name": "Dual Berettas Bandit", "price": 1000, "category": "Badges", "role_id": 1349738220056875060},
    {"id": 404, "name": "Boomstick Beast", "price": 1000, "category": "Badges", "role_id": 1349738270229270549},
    {"id": 405, "name": "Chicken Protector", "price": 1000, "category": "Badges", "role_id": 1349804769744781332},
    {"id": 406, "name": "Skin Collector", "price": 1000, "category": "Badges", "role_id": 1349803210042511360},
    {"id": 407, "name": "Entry Fragger", "price": 1000, "category": "Badges", "role_id": 1349802486445379725},
    {"id": 408, "name": "Utility Expert", "price": 1000, "category": "Badges", "role_id": 1349802368715325553},
    {"id": 409, "name": "Clutch Master", "price": 1000, "category": "Badges", "role_id": 1349804431343882340},
    {"id": 410, "name": "Chicken Chaser", "price": 1000, "category": "Badges", "role_id": 1349805088209899631},
    # XP
    {"id": 501, "name": "10 XP", "price": 10, "category": "XP", "xp": 10},
    {"id": 502, "name": "100 XP", "price": 100, "category": "XP", "xp": 100},
    {"id": 503, "name": "1000 XP", "price": 1000, "category": "XP", "xp": 1000},
    {"id": 504, "name": "10000 XP", "price": 10000, "category": "XP", "xp": 10000},
    # GIF Actions
    {"id": 601, "name": "slap", "price": 10, "category": "GIF Actions"},
    {"id": 602, "name": "kick", "price": 10, "category": "GIF Actions"},
    {"id": 603, "name": "poke", "price": 10, "category": "GIF Actions"},
    {"id": 604, "name": "hug", "price": 10, "category": "GIF Actions"},
    {"id": 605, "name": "kiss", "price": 10, "category": "GIF Actions"},
    {"id": 606, "name": "highfive", "price": 10, "category": "GIF Actions"},
    {"id": 607, "name": "tickle", "price": 10, "category": "GIF Actions"},
    {"id": 608, "name": "cs", "price": 10, "category": "GIF Actions"},
    {"id": 609, "name": "staredown", "price": 10, "category": "GIF Actions"},
]

def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, "w") as f:
            json.dump({"wallets": {}, "inventory": {}, "xp": {}}, f)
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(DATA_FILE, "w") as f:
            json.dump({"wallets": {}, "inventory": {}, "xp": {}}, f)
        return {"wallets": {}, "inventory": {}, "xp": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="shop", description="Show the shop items.")
    async def shop(self, interaction: discord.Interaction):
        currency = settings.CURRENCY_NAME
        nugget = "gold nugget"
        embed = discord.Embed(
            title="**Shop** - use /buy <item id or name> [member]",
            description="Use [member] if you want it to be a gift.",
            color=0x00ffee
        )

        # Fish equipment
        fish_equipment = (
            f"101 - Fishing Rod - 10 {currency}\n"
            f"102 - Lucky Rabbit's Foot - 100 {currency}\n"
            f"103 - Fishing Boat - 1000 {currency}"
        )
        embed.add_field(name="Fish equipment", value=fish_equipment, inline=False)

        # Archeology equipment
        archeology_equipment = (
            "201 - Indiana Jones's Map\n"
            "202 - Indiana Jones's Whip\n"
            "203 - Indiana Jones's Shovel\n"
            "204 - Indiana Jones's Brush"
        )
        embed.add_field(
            name=f"Archeology equipment - 2000 {currency}",
            value=archeology_equipment,
            inline=False
        )

        # Gold mine equipment
        gold_mine_equipment = (
            "301 - Bulldozers\n"
            "302 - Excavators\n"
            "303 - Dump Trucks\n"
            "304 - Wash Plant\n"
            "305 - Trommel\n"
            "306 - Generators & Pumps\n"
            "307 - Gold Tables & Sluices"
        )
        embed.add_field(
            name=f"Gold mine equipment - 1 {nugget}",
            value=gold_mine_equipment,
            inline=False
        )

        # Badges
        badges = (
            "401 - Deagle Dominator\n"
            "402 - AWPortunitist\n"
            "403 - Dual Berettas Bandit\n"
            "404 - Boomstick Beast\n"
            "405 - Chicken Protector\n"
            "406 - Skin Collector\n"
            "407 - Entry Fragger\n"
            "408 - Utility Expert\n"
            "409 - Clutch Master\n" 
            "410 - Chicken Chaser"
        )
        embed.add_field(
            name=f"Badges - 1000 {currency}",
            value=badges,
            inline=False
        )

        # XP
        xp = (
            f"501 - 10 XP - 100 {currency}\n"
            f"502 - 100 XP - 1000 {currency}\n"
            f"503 - 1000 XP - 10000 {currency}\n"
            f"504 - 10000 XP - 100000 {currency}"
        )
        embed.add_field(
            name="XP",
            value=xp,
            inline=False
        )

        # GIF Actions
        gif_actions = (
            "601 - slap\n"
            "602 - kick\n"
            "603 - poke\n"
            "604 - hug\n"
            "605 - kiss\n"
            "606 - highfive\n"
            "607 - tickle\n"
            "608 - cs\n"
            "609 - staredown"
        )
        embed.add_field(
            name=f"GIF Actions - 10 {currency}",
            value=gif_actions,
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Buy an item from the shop.")
    @app_commands.describe(
        item="The item id or name to buy",
        member="Give this item to another member (optional)"
    )
    async def buy(self, interaction: discord.Interaction, item: str, member: discord.Member = None):
        user_id = str(interaction.user.id)
        data = load_data()
        wallets = data.setdefault("wallets", {})
        inventory = data.setdefault("inventory", {})
        xp_data = data.setdefault("xp", {})
        nuggets = data.setdefault("nuggets", {})

        # Find item by id or name
        shop_item = None
        for i in SHOP_ITEMS:
            if str(i["id"]) == item or i["name"].lower() == item.lower():
                shop_item = i
                break
        if not shop_item:
            await interaction.response.send_message("Item not found.", ephemeral=True)
            return

        # Who receives the item
        target = member or interaction.user
        target_id = str(target.id)

        # Check wallet
        price = shop_item["price"]
        if wallets.get(user_id, 0) < price:
            price_in_nuggets = price  # Price is already in nuggets for these items
            user_nuggets = nuggets.get(user_id, 0)
            if user_nuggets < price_in_nuggets:
                await interaction.response.send_message("You don't have enough golden nuggets!", ephemeral=True)
                return

            # Subtract nuggets
            nuggets[user_id] = user_nuggets - price_in_nuggets
            save_data(data)
        else:
            # Deduct money
            wallets[user_id] -= price

        # Handle badges (roles)
        if shop_item["category"] == "Badges":
            role_id = shop_item.get("role_id", 0)
            if role_id:
                role = interaction.guild.get_role(role_id)
                if role in target.roles:
                    await target.remove_roles(role)
                    await interaction.response.send_message(f"{target.mention} already owns this badge. Badge removed!", ephemeral=False)
                else:
                    await target.add_roles(role)
                    await interaction.response.send_message(f"{target.mention} received the badge: **{role.name}**!", ephemeral=False)
                save_data(data)
                return

        # Handle GIF Actions
        if shop_item["category"] == "GIF Actions":
            gif_type = shop_item["name"].lower()
            gif_list = GIFS.get(gif_type, [])
            msg_list = CATEGORY_MESSAGES.get(gif_type, [])
            if gif_list:
                gif_url = random.choice(gif_list)
                if member:
                    sender = interaction.user.mention
                    receiver = member.mention
                else:
                    sender = receiver = interaction.user.mention
                text = random.choice(msg_list).format(sender=sender, receiver=receiver) if msg_list else f"{receiver} got a {gif_type}!"
                await interaction.response.send_message(
                    text, embed=discord.Embed().set_image(url=gif_url)
                )
            else:
                await interaction.response.send_message(f"{target.mention} performed {gif_type}!", ephemeral=False)
            save_data(data)
            return

        # Handle XP
        if shop_item["category"] == "XP":
            xp_amount = shop_item.get("xp", 0)
            xp_data[target_id] = xp_data.get(target_id, 0) + xp_amount
            # Send random XP message in leaderboard channel
            channel = self.bot.get_channel(settings.LEADERBOARD_CHANNEL_ID)
            if channel:
                msg = random.choice(XP_MESSAGES).format(member=target, amount=xp_amount)
                await channel.send(msg)
            await interaction.response.send_message(f"{target.mention} received **{xp_amount} XP**!", ephemeral=False)
            save_data(data)
            return

        # Handle normal items (add to inventory)
        inv = inventory.setdefault(target_id, [])
        inv.append(shop_item["name"])
        await interaction.response.send_message(f"{target.mention} received **{shop_item['name']}**!", ephemeral=False)
        save_data(data)

    async def cog_load(self):
        guild = discord.Object(id=settings.GUILD_ID)
        self.bot.tree.add_command(self.shop, guild=guild)
        self.bot.tree.add_command(self.buy, guild=guild)

async def setup(bot):
    await bot.add_cog(Shop(bot))