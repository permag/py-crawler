import re, urllib2
import sys
__all__ = ['crawl']


urls = []
urls_visited = []
nr = 0


def crawl(base_url, level=1):
    global urls, urls_visited, nr
    if base_url in urls_visited:
        return
    urls_visited.append(base_url)
    if level > 30:
        sys.exit(0)

    # get html
    html = get_html(base_url)
    if not html:
        return
    
    # get emails
    emails = get_emails(html)

    # get urls
    urls = get_urls(base_url, html)

    # write to file 
    nr += 1
    write_to_file(base_url, urls, emails, nr)

    # recursion
    for url in urls:
        crawl(url, level+1)


def get_html(base_url):
    data = None
    try:
        data = urllib2.urlopen(base_url)
        return data.read()
    except:
        return False


def get_urls(base_url, html):
    urls = re.findall(r'http://www.[\w.]+', html)
    urls_unique = []
    for url in urls:
        if not url in urls_unique and url != base_url:
            urls_unique.append(url)
    return urls_unique
    

def get_emails(html):
    emails = re.findall(r'[\w.]+@[\w.]+', html)
    emails_unique = []
    for email in emails:
        if not email in emails_unique:
            emails_unique.append(email)
    return emails_unique


def write_to_file(base_url, urls, emails, nr):
    with open('data.txt', 'a') as textfile:
        output = '{0}) {1}:\n'.format(nr, base_url)
        output += 'URLs:\n'
        output += ', '.join(urls)
        output += '\nE-mails:\n'
        output += ', '.join(emails) + '\n\n'
        textfile.write(output)

