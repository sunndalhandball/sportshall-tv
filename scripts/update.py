import json, re, time, urllib.request
from pathlib import Path

FEED = 'https://script.google.com/macros/s/AKfycby3CfgwPI5nvnkK4XTPxsNJzVDb0Ny8568nkbaYd_tVi_FMMdn7b9yTL1eD3Xmij--2bw/exec'
for attempt in range(3):
    try:
        with urllib.request.urlopen(FEED, timeout=40) as response:
            data = json.load(response)
        break
    except Exception:
        if attempt == 2: raise
        time.sleep(5 * (attempt + 1))

# Support common feed formats, but fail rather than erase a working list on an unexpected response.
if isinstance(data, dict):
    data = next((data[k] for k in ('images', 'files', 'bilder', 'items') if isinstance(data.get(k), list)), None)
if not isinstance(data, list):
    raise ValueError('Ukjent feedformat: forventet en liste eller images/files/bilder/items.')
images = []
for item in data:
    if isinstance(item, dict):
        item = next((item[k] for k in ('id', 'fileId', 'file_id', 'url', 'src', 'link', 'thumbnailLink') if isinstance(item.get(k), str)), None)
    if not isinstance(item, str):
        raise ValueError('Ukjent bildeoppføring i feeden.')
    item = item.strip()
    match = re.fullmatch(r'[\w-]+', item) or re.search(r'(?:/d/|[?&]id=)([\w-]+)', item)
    if not match: raise ValueError('Finner ikke Google Disk-fil-ID i en bildeoppføring.')
    file_id = match.group(1) if match.lastindex else match.group(0)
    url = 'https://lh3.googleusercontent.com/d/' + file_id
    if url not in images: images.append(url)
Path('images.json').write_text(json.dumps({'images': images}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Fant {len(images)} bilder.')
