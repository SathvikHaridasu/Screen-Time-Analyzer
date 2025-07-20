PRODUCTIVE_APPS = [
    'code', 'pycharm', 'sublime', 'excel', 'word', 'notepad', 'chrome', 'firefox', 'edge'
]
UNPRODUCTIVE_APPS = [
    'discord', 'steam', 'spotify', 'netflix', 'youtube', 'game'
]

PRODUCTIVE_SITES = [
    'wikipedia', 'stackoverflow', 'github', 'docs', 'notion'
]
UNPRODUCTIVE_SITES = [
    'facebook', 'twitter', 'instagram', 'reddit', 'tiktok', 'youtube', 'netflix'
]

def categorize_app(app_name):
    app = app_name.lower()
    if any(p in app for p in PRODUCTIVE_APPS):
        return 'Productive'
    if any(u in app for u in UNPRODUCTIVE_APPS):
        return 'Unproductive'
    return 'Neutral'

def categorize_site(url):
    url = url.lower()
    if any(p in url for p in PRODUCTIVE_SITES):
        return 'Productive'
    if any(u in url for u in UNPRODUCTIVE_SITES):
        return 'Unproductive'
    return 'Neutral' 