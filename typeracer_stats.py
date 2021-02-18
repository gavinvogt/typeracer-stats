'''
File: typeracer_stats.py
Author: Gavin Vogt
This program will scrape Typeracer for data about the given player
'''

# dependencies
import sys
import requests
import time
import traceback
import numpy
import matplotlib.pyplot as plt

class Race:
    '''
    This class represents a Race in Typeracer. Includes useful information about
    how the player performed in the race and provides read-only fields.
    '''
    __slots__ = ('_accuracy', '_num_players', '_wpm', '_place', '_timestamp',
                 '_time', '_skill_level', '_text_id', '_game_number', '_points')
    VALID_FIELDS = {'accuracy', 'num_players', 'wpm', 'place', 'timestamp',
                        'time', 'skill_level', 'text_id', 'game_number', 'points'}

    def __init__(self, *, ac, np, wpm, r, t, sl, tid, gn, pts):
        '''
        Constructs the information about a race.
        ac: float, representing the accuracy (0 - 1)
        np: int, representing the number of players in the game
        wpm: float, representing the words per minute
        r: int, representing the place finished in the race
        t: float, representing the unix timestamp of when the race occurred
        sl: str, representing the skill level
        tid: int, representing the ID of the text typed
        gn: int, representing the game number for the user (1+)
        pts: float, representing how many points the user got from the race
        '''
        self._accuracy = ac
        self._num_players = np
        self._wpm = wpm
        self._place = r
        self._timestamp = t    # time.struct_time object
        self._time = time.gmtime(t)
        self._skill_level = sl
        self._text_id = tid
        self._game_number = gn
        self._points = pts

    def __repr__(self):
        '''
        Representation of the arguments used to create this Race
        '''
        fields = (
            f"ac={repr(self._accuracy)}",
            f"np={repr(self._num_players)}",
            f"wpm={repr(self._wpm)}",
            f"r={repr(self._place)}",
            f"t={repr(self._timestamp)}",
            f"sl={repr(self._sl)}",
            f"tid={repr(self._text_id)}",
            f"gn={repr(self._game_number)}",
            f"pts={repr(self._points)}",
        )
        return f"Race({', '.join(fields)})"

    @property
    def accuracy(self):
        '''
        Accesses the `accuracy` field.
        float representing typing accuracy, between 0 and 1
        '''
        return self._accuracy

    @property
    def num_players(self):
        '''
        Accesses the `num_players` field.
        int representing number of players
        '''
        return self._num_players

    @property
    def wpm(self):
        '''
        Accesses the `wpm` field.
        float representing the wpm typing speed
        '''
        return self._wpm

    @property
    def place(self):
        '''
        Accesses the `place` field.
        int representing what place the player got
        '''
        return self._place

    @property
    def timestamp(self):
        '''
        Accesses the `timestamp` field.
        float representing the unix timestamp of the time the race occurred
        '''
        return self._timestamp

    @property
    def time(self):
        '''
        Accesses the `time` field.
        struct_time representing the time the race occurred at
        '''
        return self._time

    @property
    def skill_level(self):
        '''
        Accesses the `skill_level` field.
        str representing the skill level
        '''
        return self._skill_level

    @property
    def text_id(self):
        '''
        Accesses the `text_id` field.
        int representing the ID of the text typed
        '''
        return self._text_id

    @property
    def game_number(self):
        '''
        Accesses the `game_number` field.
        int representing the game number for the player (>= 1)
        '''
        return self._game_number

    @property
    def points(self):
        '''
        Accesses the `points` field.
        float representing the number of points the player earned
        '''
        return self._points

    @classmethod
    def is_valid_field(cls, field):
        '''
        Checks if the given field is a valid field
        '''
        return (field in cls.VALID_FIELDS)

def get_game_count(username):
    '''
    Gets the number of games the given user has played
    username: str, representing the player's username
    '''
    # Get the user's most recent race
    race = load_races(username, 1)[0]
    return race.game_number

def load_races(username, num=1):
    '''
    Loads the race data for a given user by username
    username: str, representing the player's username
    num: int, representing the number of races to load (defaults to 1)
    Return: list of Race objects
    '''
    url = f"https://data.typeracer.com/games?n={num}&universe=play&playerId=tr:{username}"
    r = requests.get(url)
    return r.json(object_hook = lambda d: Race(**d))

def graph_stats(races, username, xfield, yfield):
    '''
    Graphs the given race statistics
    races: list of Race objects
    username: str, representing the player's username
    xfield: str, representing the x field name
    yfield: str, representing the y field name
    '''
    num_races = len(races)
    stats1 = numpy.empty(num_races)
    stats2 = numpy.empty(num_races)
    for i in range(num_races):
        stats1[i] = getattr(races[i], xfield)
        stats2[i] = getattr(races[i], yfield)
    plt.plot(stats1, stats2, marker='o', linestyle='', color='green')
    plt.title(username)
    plt.xlabel(xfield)
    plt.ylabel(yfield)
    plt.show()

def get_field(num):
    '''
    Gets a field
    num: int, representing the number of the field
    '''
    field = input(f"Stat {num}: ")
    while not Race.is_valid_field(field):
        field = input(f"Stat {num}: ")
    return field

def main():
    if len(sys.argv) > 1:
        # command line arguments for what users to scrape
        usernames = sys.argv[1:]
    else:
        # ask for user input
        usernames = [input("Typeracer username: ")]

    for username in usernames:
        try:
            # Load the races
            s = time.time()
            num_races = get_game_count(username)
            races = load_races(username, num_races)
            e = time.time()
            num_races = len(races)
            print(f"Loaded {num_races} races ({e - s} seconds)")

            # Display the race stats
            fields = ", ".join(Race.VALID_FIELDS)
            print("\nAvailable fields:", fields, sep='\n')
            print("-"*len(fields) + "\n")
            xfield = get_field(1)
            yfield = get_field(2)
            graph_stats(races, username, xfield, yfield)
        except Exception as e:
            traceback.print_exc(file=sys.stderr)
            sys.stderr.write(f"Failed to load data for user `{username}`." + "\n")

if __name__ == "__main__":
    main()

