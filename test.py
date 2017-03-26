import os
import sys
import json
import re

import apiai
import requests
from flask import Flask, request, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta,date
from app import send_message

curr_time = datetime.utcnow()

send_message("1690740887619815", "hey, It's "+str(curr_time)+" now")
