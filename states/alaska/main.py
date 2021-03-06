import re
from collections import defaultdict
from bs4 import BeautifulSoup
from common import cache_request, normalize_state, diff_and_save


URL = 'http://www.elections.alaska.gov/Core/contacttheabsenteeandpetitionoffice.php'


def extract_phone_number(text):
  phone_number = ''
  match = re.search(r'(\(\d{3}\) \d{3}-\d{4})', text)
  if match is not None:
    phone_number = match.group()
    phone_number = phone_number.replace('(', '').replace(')', '')
    phone_number = phone_number.replace(' ', '-')
  return phone_number


def main():
  data = defaultdict(list)

  text = cache_request(URL)
  soup = BeautifulSoup(text, 'html.parser')

  emails = soup.find_all('a', href=re.compile(r'^mailto:'))
  for email in emails:
    email_address = ''
    if '@' in email.text:
      email_address = email.text
    else:
      email_address = email['href'].replace('mailto:', '')
    data['emails'].append(email_address)

  for p in soup.find_all('p'):
    text = p.text
    if 'Fax' in text:
      data['faxes'].append(extract_phone_number(text))
    elif 'Phone' in text or 'Toll-Free' in text:
      data['phones'].append(extract_phone_number(text))
    elif 'Absentee and Petition Office' in text:
      lines = text.split('\n')
      data['address'] = (lines[1] + lines[2]).replace('\r', ' ')


  data['locale'] = 'All'

  dict_list = []
  dict_list.append(data)

  data = normalize_state(dict_list)
  diff_and_save(data, 'public/alaska.json')


if __name__ == '__main__':
  main()
