# -*- coding: utf-8 -*-
from api import *
from linkedin import *

@server.route('/', methods=['GET'])
def index():
	linkedInAuth()
	return "cookie saved"

@server.route('/get/user-info', methods=['POST'])
def info():
	data = request.get_json()
	linkedin_data = profileDataExtractor(data["url"])
	return linkedin_data