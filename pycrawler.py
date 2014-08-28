import re, urllib2
import sys

emails = []
urls = []

def crawl(base_url, level=1):
    global emails, urls
    if level > 15:
        sys.exit(0)
    if not base_url: base_url = 'http://www.aftonbladet.se'
    data = urllib2.urlopen(base_url)
    html = data.read()
    
    # get emails
    emails = get_emails(html)

    # get urls
    urls = get_urls(base_url, html)

    # write to file 
    write_to_file(base_url, urls, emails)

    # recursion
    new_url = urls.pop()
    crawl(new_url, level+1)


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


def write_to_file(base_url, urls, emails):
    with open('data.txt', 'a') as textfile:
        output = '{}:\n'.format(base_url)
        output += 'URLs:\n'
        output += ', '.join(urls)
        output += '\nE-mails:\n'
        output += ', '.join(emails)
        textfile.write(output)





crawl(None)
