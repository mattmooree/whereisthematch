from bs4 import BeautifulSoup
import datetime
import requests
import json
import yaml

base_url = 'https://www.wheresthematch.com/live-sport-on-tv/?showdatestart='
fixtures = []

with open('interests.yaml', 'r') as file:
    yaml_data = yaml.safe_load(file)

for i in range(0, 6):
    day_raw = datetime.date.today() + datetime.timedelta(days=i)
    day = day_raw.strftime('%Y%m%d')
    r = requests.get(
        'https://www.wheresthematch.com/live-sport-on-tv/?showdatestart={}'.format(day))
    soup = BeautifulSoup(r.content, 'html.parser')
    html = list(soup.children)[2]
    body = list(html.children)[3]
    details = body.find(id='tv-listings-wrapper')
    table = body.find(lambda tag: tag.name == 'table')
    rows = table.findAll(lambda tag: tag.name == 'tr')

    for row in rows:
        channel_details = row.find('span', class_='channel-name')
        fixture_details = row.find('span', class_='fixture')
        if fixture_details:
            fixture_dict = {}
            teams = fixture_details.find_all('a')
            if len(teams) > 1:
                home_team = teams[0].find('em').get_text().strip()
                away_team = teams[1].find('em').get_text().strip()
                time_details = row.find('td', class_='start-details')
                start_time = time_details.find('em').get_text().strip()
                if home_team and away_team != 'TBC':
                    for team in yaml_data['teams']:
                        if team == home_team or team == away_team:
                            fixture_dict['Home'] = home_team
                            fixture_dict['Away'] = away_team
                            fixture_dict['Start'] = start_time
                            fixture_dict['Channel'] = channel_details.get_text(
                            ).strip()
                            fixture_dict['Date'] = day_raw.strftime('%d/%m/%Y')
                            fixtures.append(fixture_dict)
if len(fixtures) > 0:
    for fixture in fixtures:
        print("{} v {} {} {} {}".format(
            fixture['Home'],
            fixture['Away'],
            fixture['Start'],
            fixture['Date'],
            fixture['Channel']))
else:
    print('None of your teams are playing in the next 7 days.')
