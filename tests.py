import wikipedia_events_listener
import json

def test_get_title_and_comment():
    valid_data_format = '{"bot":false,"comment":"It was Law no. 135/99, not 35/99. See http://www.pgdlisboa.pt/leis/lei_mostra_articulado.php?nid=2144&tabela=leis","id":1114820056,"length":{"new":5251,"old":5213},"meta":{"domain":"en.wikipedia.org","dt":"2018-12-19T19:17:40+00:00","id":"c1b6559a-03c2-11e9-946a-1866da994783","request_id":"fc64237a-eda2-42ea-8d9a-f3559d87234f","schema_uri":"mediawiki/recentchange/2","topic":"eqiad.mediawiki.recentchange","uri":"https://en.wikipedia.org/wiki/De_facto_union_in_Portugal","partition":0,"offset":1267815388},"minor":false,"namespace":0,"parsedcomment":"It was Law no. 135/99, not 35/99. See http://www.pgdlisboa.pt/leis/lei_mostra_articulado.php?nid=2144&amp;tabela=leis","revision":{"new":874514919,"old":829311888},"server_name":"en.wikipedia.org","server_script_path":"/w","server_url":"https://en.wikipedia.org","timestamp":1545247060,"title":"De facto union in Portugal","type":"edit","user":"Jedi Friend","wiki":"enwiki"}'
    expected_title = "De facto union in Portugal"
    expected_comment = "It was Law no. 135/99, not 35/99. See http://www.pgdlisboa.pt/leis/lei_mostra_articulado.php?nid=2144&tabela=leis"
    title, comment = wikipedia_events_listener.get_title_and_comment(valid_data_format)
    assert title == expected_title
    assert comment == expected_comment

def test_check_conditions():
    valid_data_format = '{"bot":false,"comment":"It was Law no. 135/99, not 35/99. See http://www.pgdlisboa.pt/leis/lei_mostra_articulado.php?nid=2144&tabela=leis","id":1114820056,"length":{"new":5251,"old":5213},"meta":{"domain":"en.wikipedia.org","dt":"2018-12-19T19:17:40+00:00","id":"c1b6559a-03c2-11e9-946a-1866da994783","request_id":"fc64237a-eda2-42ea-8d9a-f3559d87234f","schema_uri":"mediawiki/recentchange/2","topic":"eqiad.mediawiki.recentchange","uri":"https://en.wikipedia.org/wiki/De_facto_union_in_Portugal","partition":0,"offset":1267815388},"minor":false,"namespace":0,"parsedcomment":"It was Law no. 135/99, not 35/99. See http://www.pgdlisboa.pt/leis/lei_mostra_articulado.php?nid=2144&amp;tabela=leis","revision":{"new":874514919,"old":829311888},"server_name":"en.wikipedia.org","server_script_path":"/w","server_url":"https://en.wikipedia.org","timestamp":1545247060,"title":"De facto union in Portugal","type":"edit","user":"Jedi Friend","wiki":"enwiki"}'
    json_obj = json.loads(valid_data_format)
    condition_result =  wikipedia_events_listener.check_conditions( json_obj['title'], 
                                                                    json_obj['server_url'], 
                                                                    json_obj['type'],
                                                                    json_obj['bot'])
    assert condition_result

def test_contains_noise_words():
    text = "Wikipedia:"
    assert wikipedia_events_listener.contains_noise_words(text)