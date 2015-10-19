from json import dumps as json_dumps
from bencode import bencode
from base64 import b16decode
from urllib import quote
import shelve

BACKEND_STORAGE = {}
INTERVAL = 10

def peer_remove(info_hash, peer_id):
    if info_hash in BACKEND_STORAGE:
        if peer_id in BACKEND_STORAGE[info_hash]:
            BACKEND_STORAGE[info_hash].pop(peer_id)
    

def peer_list(info_hash, peer_id=None):
    peers = []
    complete = 0
    incomplete = 0
    file_peers = BACKEND_STORAGE.get(info_hash, {})
    for peer in file_peers:
        if peer.startswith('_'):
            continue
        #peer_dict = {"id": b16decode(peer).decode('utf-8'),
        peer_dict = {#"id": peer,
                     "ip": file_peers[peer]['ip'],
                     "port": int(file_peers[peer]['port'])}
        #XXX
        # Announce part
        if True or file_peers[peer]['left'] == 0:
            if peer_id is not None and peer != peer_id:
                peers.append(peer_dict)
        # Scrape part
        if file_peers[peer]['left'] == 0:
            complete += 1
        else:
            incomplete += 1
    downloaded = file_peers.get('_downloaded', 0)
    stats = {'complete': complete,
             'downloaded': downloaded,
             'incomplete': incomplete}
    return peers, stats

def peer_update(info_hash, peer_id, infos):
    file_peers = BACKEND_STORAGE.get(info_hash, {})
    peer_infos = file_peers.get(peer_id, infos)
    file_peers.update({peer_id: infos})
    BACKEND_STORAGE.update({info_hash: file_peers})

def file_complete(info_hash):
    file_peers = BACKEND_STORAGE.get(info_hash, {})
    file_peers['_downloaded'] = file_peers.get('_downloaded', 0) + 1
    BACKEND_STORAGE.update({info_hash: file_peers})
    

def announce(query):
    print("===== QUERY =====")
    print(json_dumps(query, indent=2))
    error = False
    info_hash = query.pop('info_hash')
    peer_id = query.pop('peer_id')
    peer_update(info_hash, peer_id, query)
    if query.get("event") == "stopped":
        peer_remove(info_hash, peer_id)
    if query.get("event") == "completed":
        file_complete(info_hash)
    peers, stats = peer_list(info_hash, peer_id)
    response = {"interval": INTERVAL,
                "peers": peers}

    encoded_response = bencode(response)
    return error, encoded_response

def scrape(query):
    raise
    error = False
    #info_hash = query.pop('info_hash')
    #peers, stats = peer_list(info_hash)
    #response = {"files": {query['info_hash']: stats}}
    response = {"files": {}}

    encoded_response = bencode(response)
    return error, encoded_response

