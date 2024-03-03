from googleapiclient.discovery import build
import socket
from httplib2 import socks
import httplib2
from urllib.parse import urlparse, parse_qs
 
httpProxy = httplib2.Http(proxy_info = httplib2.ProxyInfo(socks.PROXY_TYPE_SOCKS5, 'localhost', 9150))
api_key = ''
youtube = build('youtube', 'v3', developerKey=api_key,  http = httpProxy)
    
def get_video_id(url):
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None
 
def get_video_title(urls):
        video_titles_list = ""
        video_ids = []
        for url in urls:
            video_ids.append(get_video_id(url))
        request = youtube.videos().list(part = 'snippet', id = ','.join(video_ids))
        response = request.execute()
        youtube.close()
        index_number = 1
        for item in response['items']:
                video_title = item['snippet']['title']
                video_titles_list += f'{index_number}. {video_title}\n'
                index_number += 1
        return video_titles_list
 
class RequestPage():
 
    def __init__(self, videos_list: list, next_page_token = None, prev_page_token = None):
        self.videos_list = videos_list
        self.next_page_token = next_page_token
        self.prev_page_token = prev_page_token
 
def get_video_info_by_keyword(key: str, page_token = None):
    videos_info_list = []
    if page_token:
        request = youtube.search().list(part = 'snippet', q = key, type = 'video', maxResults = 5, pageToken = page_token)
    else:
        request = youtube.search().list(part = 'snippet', q = key, type = 'video', maxResults = 5)
    try: 
        response = request.execute()
    except Exception as e:
        print(e)
        page = RequestPage(videos_info_list, None, None)
        return page 
    youtube.close()
 
    for item in response['items']:
        video_title = item['snippet']['title']
        video_id = item['id']['videoId']
 
        videos_info_list.append({
            'title' : video_title, 
            'id' : video_id
            })
    if 'nextPageToken' in response and 'prevPageToken' in response:
        page = RequestPage(videos_info_list, response['nextPageToken'], response['prevPageToken'])
    elif not 'nextPageToken' in response and 'prevPageToken' in response:
        page = RequestPage(videos_info_list, response['prevPageToken'])
    elif 'nextPageToken' in response and not 'prevPageToken' in response:
        page = RequestPage(videos_info_list, response['nextPageToken'])
    elif not 'nextPageToken' in response and not 'prevPageToken' in response:
        page = RequestPage(videos_info_list)
    else:
        raise ValueError("Неправильный запрос")
    return page
 