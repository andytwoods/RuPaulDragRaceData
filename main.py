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
            'description': '',
            'guest_judges': None,
            'mini_challenge': None,
            'main_challenge': None,
            'challenge_winner': None,
            'bottom_two': None,
            'lipsync_song': None,
            'eliminated': None,
        }

    page = requests.get(get_season_url(season))
    soup = BeautifulSoup(page.content, "html.parser")
    current_episode_info = gen_episode_info()
    episodes = []

    for table in soup.find_all("table", class_='wikiepisodetable'):
        table_body = next(table.children)
        for _row in table_body.children:

            if type(_row) is NavigableString:
                continue

            if not _row.has_attr('class'):
                continue

            is_info_row = 'vevent' in _row.get('class')
            if is_info_row:
                current_episode_info = gen_episode_info()
                cols = list(_row.children)
                current_episode_info['number_overall'] = int(cols[0].text)
                current_episode_info['number_in_season'] = int(cols[1].text)
                current_episode_info['title'] = cols[2].text

                date_str: str = cols[3].text
                first_bracket = date_str.find('(')
                last_bracket = date_str.find(')')
                date_str = date_str[first_bracket + 1: last_bracket]
                current_episode_info['date_aired'] = datetime(*[int(x) for x in date_str.split('-')])
                continue

            is_header_row = 'expand-child' in _row.get('class')
            if is_header_row:

                for subsection in _row:

                    if not hasattr(subsection, 'children'):
                        continue

                    if subsection.name != 'td':
                        continue

                    if subsection.has_attr('class') and 'description' in subsection.get('class'):
                        child_children = subsection.children
                        for el in child_children:
                            if not hasattr(el, 'type'):
                                continue
                            if el.name == 'p':
                                if len(el.text) > 5:
                                    current_episode_info['description'] += ''.join(el.text.splitlines())
                            elif el.name == 'ul':
                                for list_el in el.children:
                                    el_text: str = list_el.text
                                    el_text_lower = el_text.lower()

                                    if 'guest' in el_text_lower and 'judge' in el_text_lower:
                                        current_episode_info['guest_judges'] = el_text
                                    elif 'mini' in el_text_lower and 'challenge' in el_text_lower:
                                        current_episode_info['mini_challenge'] = el_text

                                    elif 'main' in el_text_lower and 'challenge' in el_text_lower:
                                        current_episode_info['main_challenge'] = el_text
                                    elif ('challenge' in el_text_lower and 'winner' in el_text_lower) or \
                                            ('winner' in el_text_lower and 'rupaul' in el_text_lower):
                                        current_episode_info['challenge_winner'] = el_text
                                    elif 'bottom' in el_text_lower and 'two' in el_text_lower:
                                        current_episode_info['bottom_two'] = el_text
                                    elif 'lip' in el_text_lower and 'sync' in el_text_lower and 'song' in el_text_lower:
                                        current_episode_info['lipsync_song'] = el_text
                                    elif 'eliminated' in el_text_lower or \
                                            ('runner' in el_text_lower and 'up' in el_text_lower):
                                        current_episode_info['eliminated'] = el_text

                episodes.append(current_episode_info)

    for episode in episodes:
        print(episode)


get_season_data(3)
