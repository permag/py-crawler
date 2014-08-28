import re, urllib2
from timeout import timeout
import sys

__all__ = ['crawl']


urls = []
urls_visited = []
excluded = ['favicon', '.ico', '.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '#', '?']
nr = 1
output = False
filename = 'data.txt'


def crawl(base_url, filename=None, **kwargs):
    global urls, urls_visited, nr, output
    if kwargs:
        if kwargs['output'] is True:
            output = True

    if base_url in urls_visited:
        return
    urls_visited.append(base_url)

    # get html
    html = get_html(base_url)
    if not html:
        return
    
    # get emails
    emails = get_emails(html)

    # get urls
    urls = get_urls(base_url, html)

    # write to file 
    write_to_file(base_url, urls, emails, nr)

    # print
    if output:
        print '{0}\t{1}\t{2}'.format(nr, len(urls), len(emails))
    
    # count
    nr += 1

    # recursion
    for url in urls:
        crawl(url)


@timeout(1)
def get_html(base_url):
    data = None
    try:
        data = urllib2.urlopen(base_url)
        return data.read()
    except:
        return False


def get_urls(base_url, html):
    global excluded
    urls = re.findall(r'href="[\'"]?([^\'" >]+)', html)
    urls_unique = []
    for url in urls:
        if not url in urls_unique and url != base_url and not any(word in url for word in excluded):
            if url[:7] == 'http://' or url[:8] == 'https://' or url[:3] == 'www':
                urls_unique.append(url)
            elif len(url) > 100:
                continue
            elif url[:3] == '../':
                url = url[3:]
            elif url[:2] == './':
                url = url[2:]
            elif url[0] == '/' or '.':
                url = url[1:]
            else:                
                urls_unique.append('{0}{1}'.format(base_url, url))
    return urls_unique
    

def get_emails(html):
    emails = re.findall(r'[\w.]+@[\w.]+', html)
    emails_unique = []
    for email in emails:
        if not email in emails_unique:
            emails_unique.append(email)
    return emails_unique


def write_to_file(base_url, urls, emails, nr):
    global filename
    with open(filename, 'a') as textfile:
        output = '{0}) {1}:\n'.format(nr, base_url)
        output += 'URLs: (%d)\n' % len(urls)
        output += ', '.join(urls)
        output += '\nE-mails: (%d)\n' % len(emails)
        output += ', '.join(emails) + '\n\n'
        textfile.write(output)


def main():
    global filename
    if len(sys.argv) > 2:
        url = sys.argv[1]
        filename = sys.argv[2]
    elif len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print 'Use URL and textfile as argument: python pycrawler.py http://www.domain.com filename.txt'
        sys.exit(0)
    print 'Nr.\tURLs\tE-mails'
    crawl(url, filename, output=True)



if __name__ == '__main__':
    main()
