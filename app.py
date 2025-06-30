import os
from pprint import pprint
from pymongo import MongoClient
from youtool import YouTube
from youtool.utils import simplify_vtt
from dotenv import load_dotenv
import datetime

def load_config(env_path='.env'):
    load_dotenv(env_path)
    config = {
        'api_keys': os.getenv('YOUTUBE_API_KEYS', '').split(','),
        'channel_url': os.getenv('CHANNEL_URL'),
        'mongo_uri': os.getenv('MONGO_URI'),
        'db_name': os.getenv('DB_NAME'),
        'since': os.getenv('SINCE'),
        'transcription_lang': os.getenv('TRANSCRIPTION_LANG', 'en'),
        'transcription_dir': os.getenv('TRANSCRIPTION_DIR', './transcricoes')
    }
    missing = [k for k in ['api_keys', 'channel_url'] if not config[k] or (k == 'api_keys' and not any(config['api_keys']))]
    if missing:
        raise EnvironmentError(f"Missing required config(s) in .env: {', '.join(missing)}")
    config['api_keys'] = [k.strip() for k in config['api_keys'] if k.strip()]
    return config


def connect_mongo(uri: str, db_name: str):
    client = MongoClient(uri)
    return client[db_name]


def ensure_indexes(db):
    db.channels.create_index('channel_id', unique=True)
    db.videos.create_index('video_id', unique=True)
    db.comments.create_index([('video_id', 1), ('comment_id', 1)], unique=True)
    db.transcriptions.create_index('video_id', unique=True)
    db.livechats.create_index('video_id', unique=True)
    db.superchats.create_index('video_id', unique=True)


def main():
    cfg = load_config()
    since_dt = None
    if cfg['since']:
        val = cfg['since'].rstrip('Z')
        try:
            since_dt = datetime.datetime.fromisoformat(val + '+00:00')
        except Exception:
            raise ValueError("Formato inválido em SINCE no .env. Use ISO8601, ex: 2024-01-01T00:00:00Z")

    yt = YouTube(cfg['api_keys'])
    db = connect_mongo(cfg['mongo_uri'], cfg['db_name'])
    ensure_indexes(db)

    vids = armazenarVideos(yt, db, playlist_id, since_dt)
    limited_vids = vids[:10]

if __name__ == '__main__':
    main()
