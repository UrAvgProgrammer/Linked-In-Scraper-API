from flask import Flask, jsonify, request


server = Flask(__name__)
server.config['JSON_AS_ASCII'] = False

from api.app import *