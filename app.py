import os, sys
from flask import Flask, request
from utils import wit_response
from pymessenger import Bot

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAARTH1QxusMBAKPcjMNpD28k4ShrXdOdq4dRguTZBRKWxdHcqwqVMWh3TKlDyQgR1ZAXpG2ZCqhVbRmxsmNhT1xIMCwWDmxnrOZBKzKdNTHgdERUirISQ1DUGXALt95UdVtejUaQqRGBkc1bPJd0S7r1a3AdpoQTxZAzH3NVAxAZDZD"

bot = Bot(PAGE_ACCESS_TOKEN)

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
	
	if data['object'] == 'page':
		for entry in data['entry']:
			for messaging_event in entry['messaging']:

				# IDs
				sender_id = messaging_event['sender']['id']
				recipient_id = messaging_event['recipient']['id']

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
					for entity_item in entity:
						try:
							if entity_item[0] == 'number':
								for number in entity_item[1]:
									numbers.append(number)
						except:
							bot.send_text_message(sender_id, "Neispravno uneta kolicina hrane")
						try:
							if entity_item[0] == 'size':
								for size in entity_item[1]:
									sizes.append(size)
						except:
							bot.send_text_message(sender_id, "Neispravno uneta velicina narudzbine")
						try:
							if entity_item[0] == 'food_type':
								for food_type in entity_item[1]:
									foods.append(food_type)
						except:
							bot.send_text_message(sender_id, "Neispravno unet naziv hrane")
						if entity_item[0] == 'agenda_type':
							#odgovor da ili ne
							resp = entity_item[1][0]
					response = "Vasa porudzbina je\n"
					strbuf = ""
					try:
						for i in range(len(numbers)):
							strbuf = strbuf + "{0}X {1} {2}\n".format(numbers[i], sizes[i], foods[i])
							response = response + strbuf
						if strbuf == "":
							response = "Molimo ponovite narudzbinu"

						bot.send_text_message(sender_id, response)
					except:
						bot.send_text_message(sender_id, "Molim unesite ispravnu narudzbinu\nFORMAT: KOLICINA VELICINA JELO")
	# except:			
	return "ok", 200

def log(message):
	print(message)
	sys.stdout.flush()

if __name__ == "__main__":
	app.run()