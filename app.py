import os
from pprint import pprint
from pymongo import MongoClient
from youtool import YouTube
from youtool.utils import simplify_vtt
from dotenv import load_dotenv
import datetime
import json
from googleapiclient.discovery import build

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

def buscarEArmazenarCanal(yt: YouTube, db, channel_url: str):
    channel_id = yt.channel_id_from_url(channel_url)
    info = list(yt.channels_infos([channel_id]))[0]
    record = {
        'channel_id': channel_id,
        'title': info.get('title'),
        'description': info.get('description'),
        'custom_url': info.get('custom_url'),
        'thumbnails': info.get('thumbnails'),
        'stats': info.get('statistics'),
    }
    db.channels.update_one({'channel_id': channel_id}, {'$set': record}, upsert=True)
    return channel_id, info.get('playlist_id')

def armazenarVideos(yt, db, playlist_id, since_dt):
    videos = []
    for video in yt.playlist_videos(playlist_id):
        if since_dt:
            published = video.get('publishedAt')
            if published and published < since_dt.isoformat():
                continue
        vid = video.get('video_id') or video.get('id') or video.get('videoId')
        if vid:
            videos.append(vid)
            db.videos.update_one(
                {'video_id': vid},
                {'$set': {**video, 'video_id': vid}},
                upsert=True
            )
        if len(videos) >= 10:
            break
    return videos

def coletarComentarios(yt: YouTube, db, video_ids):
    for vid in video_ids:
        for c in yt.video_comments(vid):
            cid = c.get('id')
            if not cid:
                continue
            rec = {
                'video_id':          vid,
                'comment_id':        cid,
                'author':            c.get('author'),
                'author_profile':    c.get('author_profile_image_url'),
                'author_channel_id': c.get('author_channel_id'),
                'text':              c.get('text'),
                'likes':             c.get('likes'),
                'published_at':      c.get('published_at'),
                'replies':           c.get('replies'),
            }
            db.comments.update_one(
                {'video_id': vid, 'comment_id': cid},
                {'$set': rec},
                upsert=True
            )

        print(f"Comentários salvos para vídeo {vid}")

def armazenarTranscricoes(yt: YouTube, db, video_ids, lang, out_dir):
    try:
        import yt_dlp
    except ModuleNotFoundError:
        raise ModuleNotFoundError("Para baixar transcrições, instale: pip install yt-dlp")
    try:
        import webvtt
    except ModuleNotFoundError:
        raise ModuleNotFoundError("Para processar VTT, instale: pip install webvtt-py")

    os.makedirs(out_dir, exist_ok=True)
    for vid in video_ids:
        for status in yt.download_transcriptions(videos_ids=[vid], language_code=lang, path=out_dir, batch_size=1):
            print(status)

        path = os.path.join(out_dir, f"{vid}.{lang}.vtt")
        if not os.path.exists(path):
            print(f"⚠️ Transcrição não encontrada para vídeo {vid}")
            continue

        with open(path, encoding='utf-8') as f:
            simple = simplify_vtt(f.read())

        db.transcriptions.update_one(
            {'video_id': vid},
            {'$set': {'video_id': vid, 'transcription': simple}},
            upsert=True
        )
        print(f"Transcrição salva para vídeo {vid}")

def fetch_video_statistics(youtube_api_key, video_id):
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    request = youtube.videos().list(
        part='statistics',
        id=video_id
    )
    response = request.execute()
    items = response.get('items', [])
    if not items:
        return None
    return items[0].get('statistics')

def armazenarDetalhesVideos(yt: YouTube, db, video_ids, api_key):
    for info in yt.videos_infos(video_ids):
        vid = info.get('video_id') or info.get('id')
        if not vid:
            continue
        
        stats = info.get('statistics')
        if not stats:
            stats = fetch_video_statistics(api_key, vid)
        
        record = {
            'video_id': vid,
            'title': info.get('title'),
            'description': info.get('description'),
            'publishedAt': info.get('publishedAt'),
            'duration': info.get('duration'),
            'statistics': stats,
            'tags': info.get('tags'),
            'categoryId': info.get('categoryId'),
            'status': info.get('status'),
        }
        db.videos.update_one({'video_id': vid}, {'$set': record}, upsert=True)
        print(f"📄 Detalhes armazenados para vídeo {vid}")

def exportar_estatisticas_json(db, output_path="estatisticas_videos.json"):
    documentos = db.videos.find({}, {
        "_id": 0,
        "video_id": 1,
        "title": 1,
        "publishedAt": 1,
        "statistics": 1
    })

    data = []
    print("\n📦 Exportando estatísticas dos vídeos:\n")
    for doc in documentos:
        stats = doc.get("statistics") or {}
        info = {
            "video_id": doc.get("video_id"),
            "title": doc.get("title"),
            "publishedAt": doc.get("publishedAt"),
            "viewCount": stats.get("viewCount"),
            "likeCount": stats.get("likeCount"),
            "commentCount": stats.get("commentCount")
        }
        data.append(info)

        print(f"✅ Exportado: {info['title']} (views: {info['viewCount']}, likes: {info['likeCount']})")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 Exportação concluída. Arquivo salvo em: {output_path}")

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

    channel_id, playlist_id = buscarEArmazenarCanal(yt, db, cfg['channel_url'])
    vids = armazenarVideos(yt, db, playlist_id, since_dt)
    limited_vids = vids[:10]
    coletarComentarios(yt, db, limited_vids)
    armazenarDetalhesVideos(yt, db, limited_vids, cfg['api_keys'][0])
    armazenarTranscricoes(yt, db, limited_vids, cfg['transcription_lang'], cfg['transcription_dir'])
    exportar_estatisticas_json(db)

if __name__ == '__main__':
    main()
