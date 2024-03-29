import os
import json

STORAGE_DIR = os.getenv('STORAGE_DIR', 'notifications')

def store(msg_id: str, msg: dict, reference_id: str = None):
    msg_fn = msg_id + '.json'
    subdir = msg_id # the 'message thread'
    if reference_id:
        # case when it is a 'follow up' message in a conversation
        subdir = reference_id
    dir = os.path.join(STORAGE_DIR, subdir)
    os.makedirs(dir, exist_ok=True)
    fn = os.path.join(dir, msg_fn)
    content = json.dumps(msg, indent=4)
    with(open(fn, 'w')) as f:
        f.write(content)
