import os, sys, urllib.request as urrq, json
from flask import Flask, request
from utils import wit_response
from pymessenger import Bot
import re


app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAARTH1QxusMBANFxjBBZANfwistYiC228GjLaZB0hJOP8g0g6wQfrl2fA0HdlcEmnGZBeBuYP1C8AZAoEtpfdzxWcEYNZCbUzoUsG7tvZCLG7ZCwWpZBGVuHSfowjzZC9dV7BYhYuzFZC4rVpwnmcxNlRbS7RiLJQ4JiJWpCVaFNhkWwZDZD"
GOOGLE_MAPS_KEY = "AIzaSyDDNH9QxrBuMQ1rYsz-yGDgoJQyWCe-tRk"

bot = Bot(PAGE_ACCESS_TOKEN)
order = None
vreme_cekanja = None

@app.route('/', methods=['GET'])
def verify():
	#Webhook verification
	if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
		if not request.args.get("hub.verify_token") == "hello":
			return "Verification token mismatch", 403
		return request.args["hub.challenge"], 200
	return "Hello World", 200

@app.route('/', methods=['POST'])
def webhook():
	data = request.get_json()
	log(data)
	# try:

	response = None
	numbers = []
	sizes = []
	foods = []
	lok = 0

	if data['object'] == 'page':
		for entry in data['entry']:
			for messaging_event in entry['messaging']:

				# IDs
				sender_id = messaging_event['sender']['id']
				recipient_id = messaging_event['recipient']['id']
				latitude = None
				longtitude = None
				try:
					latitude = messaging_event['message']['attachments'][0]['payload']['coordinates']['lat']
					longtitude = messaging_event['message']['attachments'][0]['payload']['coordinates']['long']
					
					url = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=44.798373,'
					url += '20.470345&destinations={},{}&key={}'.format(str(latitude), str(longtitude), GOOGLE_MAPS_KEY)
					#Sends the request and reads the response.
					response = urrq.urlopen(url).read()
					#Loads response as JSON
					directions = json.loads(response)
					print(directions['rows'][0]['elements'][0]['duration']['text'])
					waiting_time = directions['rows'][0]['elements'][0]['duration']['text']
					waiting_time = ''.join(x for x in waiting_time if x.isdigit())
					waiting_time = int(waiting_time) + 15
					vreme_cekanja = waiting_time
					bot.send_text_message(sender_id, "Procenjeno vreme cekanja: " + str(waiting_time) + " minuta")
					lok = 1
				except:
					pass

				if messaging_event.get('message'):
					# Extracting text message
					if 'text' in messaging_event['message']:
						messaging_text = messaging_event['message']['text']
					else:
						messaging_text = 'no text'

					# Response
					resp = None
					# [('number', ['2', '1', '2']), ('size', ['veliku', 'srednju', 'malu']), ('food_type', ['kapricoza', 'fresh margherita', 'double pepperoni'])]
					entity = wit_response(messaging_text)
					
					if len(entity) == 0:
						pattern = '([A-Za-z]+\s+)+[\d]+'
						r = re.match(pattern, messaging_text)
						print(r)
						if r:
							try:
								messaging_text = messaging_text.replace(' ', '+')
								messaging_text.replace('ć', 'c')

								print(messaging_text)
								url = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=44.798373,'
								url += '20.470345&destinations={}&key={}'.format(messaging_text, GOOGLE_MAPS_KEY)
								#Sends the request and reads the response.
								response = urrq.urlopen(url).read()
								#Loads response as JSON
								directions = json.loads(response)
								print(directions['rows'][0]['elements'][0]['duration']['text'])
								waiting_time = directions['rows'][0]['elements'][0]['duration']['text']
								waiting_time = ''.join(x for x in waiting_time if x.isdigit())
								waiting_time = int(waiting_time) + 15
								vreme_cekanja = waiting_time
								bot.send_text_message(sender_id, "Procenjeno vreme cekanja: " + str(waiting_time) + " minuta")
								lok = 1
							except:
								bot.send_text_message(sender_id, "Neispravna adresa")

					for entity_item in entity:
						try:
							if entity_item[0] == 'number':
								for number in entity_item[1]:
									numbers.append(number)
							elif entity_item[0] == 'size':
								for size in entity_item[1]:
									sizes.append(size)
							elif entity_item[0] == 'food_type':
								for food_type in entity_item[1]:
									foods.append(food_type)
							elif entity_item[0] == 'potvrda':
								#odgovor da ili ne
								resp = entity_item[1][0]
								if resp == "da":
									bot.send_text_message(sender_id, "Molimo posaljite Vasu tacnu lokaciju za dostavu, kao lokaciju ili kao tacnu adresu")
									lok = 1
						except:
							bot.send_text_message(sender_id, "Molim unesite ispravnu narudzbinu\nFORMAT: KOLICINA VELICINA JELO")

					response = "Vasa porudzbina je\n"
					strbuf = ""

					try:
						for i in range(len(numbers)):
							strbuf = strbuf + "{0}X {1} {2}\n".format(numbers[i], sizes[i], foods[i])
							response = response + strbuf
							order = response
						if strbuf == "":
							if lok == 0:
								bot.send_text_message(sender_id, "Molim unesite ispravnu narudzbinu\nFORMAT: KOLICINA VELICINA JELO")
								bot.send_text_message(sender_id, "Molim te imaj u vidu da ne razumem srpska slova, moras da mi pises u alfabetu :(")
						else:
							bot.send_text_message(sender_id, response)
							bot.send_text_message(sender_id, "Da li sam ispravno preneo Vasu narudzbinu?")
						lok = 0
					except:
						bot.send_text_message(sender_id, "Molim unesite ispravnu narudzbinu\nFORMAT: KOLICINA VELICINA JELO")
						bot.send_text_message(sender_id, "Molim te imaj u vidu da ne razumem srpska slova, moras da mi pises u alfabetu :(")
	# except:			
	return "ok", 200

def log(message):
	print(message)
	sys.stdout.flush()

if __name__ == "__main__":
	app.run()