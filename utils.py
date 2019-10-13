from wit import Wit

access_token = "NJS5DIBBEBVT5ATXN5LHPZZAF3ITXRZH"
client = Wit(access_token = access_token)

def wit_response(message_text):
	resp = client.message(message_text)
	entity = []
	value_list = []

	try:
		for entity_item in list(resp['entities']):
			# if entity_item == 'agenda_entry':
			# 	return entity_item
			for value_item in resp['entities'][entity_item]:
				value = value_item['value']
				value_list.append(value)
			entity.append((entity_item, value_list))
			value_list = []
	except:
		pass
	return entity