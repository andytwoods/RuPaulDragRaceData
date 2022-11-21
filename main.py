from datetime import datetime

import requests
from bs4 import BeautifulSoup, Tag, NavigableString


def get_season_url(season: int):
    return f"https://en.wikipedia.org/wiki/RuPaul%27s_Drag_Race_(season_{season})"



def get_season_data(season):

    def gen_episode_info():
        return {
            'number_in_season': None,
            'number_overall': None,
            'title': None,
            'date_aired': None,
            'description':  '',
            'guest_judges':  None,
            'mini_challenge':  None,
            'main_challenge':  None,
            'challenge_winner':  None,
            'bottom_two':  None,
            'lipsync_song':  None,
            'eliminated':  None,
        }

    page = requests.get(get_season_url(season))
    soup = BeautifulSoup(page.content, "html.parser")
    current_episode_info = gen_episode_info()
    episodes = []

    for table in soup.find_all("table", class_='wikiepisodetable'):
        table_body = next(table.children)
        for _row in table_body.children:
            is_header_row = 'Original air date' in _row.text

            if is_header_row:
                if current_episode_info['bottom_two']:
                    episodes.append(current_episode_info)
                    current_episode_info = gen_episode_info()


            for child in _row:

                if not hasattr(child, 'children'):
                    continue


                if not current_episode_info['title']:  # we dont have header info yet
                    if child.name == 'th':
                        id_ = child.get('id', '')
                        if id_.startswith('ep'):
                            current_episode_info['number_overall'] = int(id_[2:])

                            subsequent = next(_row.children)
                            current_episode_info['number_in_season'] = int(next(subsequent.children).get('id'))

                            subsequent = next(_row.children)  # title
                            current_episode_info['title'] = subsequent.text

                            subsequent = next(_row.children)  # date
                            date_str: str = subsequent.text
                            first_bracket = date_str.find('(')
                            last_bracket = date_str.find(')')

                            date_str = date_str[first_bracket+1: last_bracket]
                            current_episode_info['date_aired'] = datetime(*[int(x) for x in date_str.split('-')])

                else:  # we have header info already
                    if child.name == 'td':
                        if child.has_attr('class') and 'description' in child.get('class'):
                            child_children = child.children
                            for el in child_children:
                                if not hasattr(el, 'type'):
                                    continue
                                if el.name == 'p':
                                    if len(el.text) > 5:
                                        current_episode_info['description'] += ''.join(el.text.splitlines())
                                else:
                                    el_text: str = el.text
                                    if 'Guest Judges' in el_text:
                                        current_episode_info['guest_judges'] = el_text
                                    elif 'Mini-Challenge' in el_text:
                                        current_episode_info['mini_challenge'] = el_text[len('mini_challenge')+1:]
                                    elif 'Main Challenge' in el_text:
                                        current_episode_info['main_challenge'] = el_text[len('main_challenge')+1:]
                                    elif 'Challenge Winner' in el_text:
                                        current_episode_info['challenge_winner'] = el_text[len('challenge_winner')+1:]
                                    elif 'bottom_two' in el_text:
                                        current_episode_info['bottom_two'] = el_text[len('bottom_two')+1:]
                                    elif 'Lip-Sync Song' in el_text:
                                        current_episode_info['lipsync_song'] = el_text[len('lip-sync_song')+1:]
                                    elif 'Eliminated' in el_text:
                                        current_episode_info['eliminated'] = el_text[len('eliminated')+1:]

    print(episodes)







get_season_data(1)
