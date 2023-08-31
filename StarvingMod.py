import random
import numpy as np
import pandas as pd
import discord
from discord.ext import commands
from discord.utils import get
import shutil, pathlib, os, sys
from datetime import datetime as dt, timedelta as timeD
import time

def getCurrentUTC():
	return int(time.mktime(dt.now().timetuple()))

def checkIfStarved(player):
	""" Gets current time and returns True if current time is greater than starve time for the passed in player."""
	if getCurrentUTC() >= int(player[6]) and int(player[6]) != 0:
		return True
	else:
		return False

def findNextStarve(player, next_starve_time, next_starve_player):
	""" Checks if a player is the next player to starve. """
	if int(player[6]) < next_starve_time and int(player[6]) != 0 and str(player[5]) == 'Zombie':
		next_starve_player = player
		next_starve_time = int(player[6])
	return next_starve_time, next_starve_player
