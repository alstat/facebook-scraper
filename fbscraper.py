# Script to read Facebook Page posts using Facebook Graph API
# Input
# @ FACEBOOK_PAGE_ID
# @ ACCESS TOKEN - valid and not expired
import requests
import key_config as config
import simplejson as json

def read_posts(url, source):

    try:
        print('URL: {}'.format(url))
        content = requests.get(url, verify = False).json()

    except Exception:
        return {'data': [], 'next': ''}

    if 'posts' in content:
        posts = content['posts']['data']

        try: 
            next_url = content['posts']['paging']['next']
        except Exception: 
            next_url = ''

    elif 'data' in content:
        posts = content['data']

        try: 
            next_url = content['paging']['next']
        except Exception: 
            next_url = ''

    else:
        return {'data': [], 'next': ''}

    data = []
    for post in posts:

        try:
            print('Created time: {}'.format(post['created_time']))
            # if post['created_time'][:4] != '2010':
            #     return {'data': data, 'next': ''}

            print(post)

            article = {
                'id': post['id'],
                'timestamp' : post['created_time'],
                'summary' : post['message'],
                'link' : post['link'],
                'type' : post['status_type'],
                'likes' : post['like']['summary']['total_count'],
                'comments_count' : post['comments']['summary']['total_count'],
                'full_picture' : post['full_picture'],
                'thumb_picture' : post['picture'],
                'permalink_url' : post['permalink_url'],
                'love': post['love']['summary']['total_count'],
                'haha': post['haha']['summary']['total_count'],
                'wow' : post['wow']['summary']['total_count'],
                'sad' : post['sad']['summary']['total_count'],
                'angry' : post['angry']['summary']['total_count']
            }

            if post['comments']['data'] != []:
                comments = []
                for comment in post['comments']['data']:
                    comments += [comment['message']]
                article['comments'] = comments
            else:
                article['comments'] = []

        except Exception as e:
            continue

        try:
            article['shares'] = post['shares']['count']
        except Exception:
            article['shares'] = 0

        try:

            if 'subattachments' in post['attachments']['data']:
                article['attachments'] = post['attachments']['data']['subattachments']
            else:
                article['attachments'] = post['attachments']['data']

            article['description'] = article['attachments'][0]['description']
            article['title'] = article['attachments'][0]['title']

        except Exception as e:
            article['attachments'] = []
            article['description'] = ""
            article['title'] = ""

        # Add news source
        article['source'] = source
        data += [article]

    return {'data' : data, 'next' : next_url}

def scrape_page(FACEBOOK_PAGE_ID, ACCESS_TOKEN):
    URL = 'https://graph.facebook.com/v2.12/' + FACEBOOK_PAGE_ID +\
          '?fields=posts.limit(100)' \
          '{id,created_time,message,attachments,link,permalink_url,shares,%20status_type,%20comments.limit(1000).summary(true),reactions.type(LIKE).summary(total_count).as(like),reactions.type(LOVE).summary(total_count).as(love),reactions.type(HAHA).summary(total_count).as(haha),reactions.type(WOW).summary(total_count).as(wow),reactions.type(SAD).summary(total_count).as(sad),reactions.type(ANGRY).summary(total_count).as(angry),full_picture,picture}&access_token=' + ACCESS_TOKEN + '&pretty=0;'

    data = read_posts(URL, FACEBOOK_PAGE_ID)
    print(data)

    articles = data['data']
    next_link = data['next']

    while next_link != '':
        data = read_posts(next_link, FACEBOOK_PAGE_ID)
        articles = articles + data['data']
        next_link = data['next']

    return articles

if __name__ == '__main__':

    output = scrape_page("welovekarylle", config.ACCESS_TOKEN)
    with open("output_fb.json", 'w') as f:
        json.dump(output, f)
