from timeout import timeout
from db import Database
import re, urllib2
import sys

__all__ = ['crawl']


class Crawler:

    def __init__(self):
        self._urls = []
        self._emails = []
        self._urls_visited = []
        self._excluded = ['favicon', '.ico', '.css', '.js', '.jpg', 
                         '.jpeg', '.png', '.gif', '#', '?', '.pdf',
                         '.doc']
        self._nr = 0
        self._output = False
        self._filename = 'data.txt'


    @property
    def nr(self):
        return self._nr


    def crawl(self, base_url, filename=None, **kwargs):
        base_url = base_url.strip()
        self._nr = 0
        if kwargs:
            if kwargs['output'] is True:
                self._output = True
        return self.do_crawl(base_url)


    def do_crawl(self, base_url):
        if base_url in self._urls_visited:
            return
        self._urls_visited.append(base_url)

        # get html
        html = self.get_html(base_url)
        if not html:
            return
        
        # count
        self._nr += 1
        
        # get page title
        title = self.get_page_title(html)

        # get meta keywords
        keywords = self.get_meta_keywords(html)

        # get emails
        self._emails = self.get_emails(html)

        # get urls
        self._urls = self.get_urls(base_url, html)

        # write to db: url, title, keywords, date
        self.write_to_db(base_url, title, keywords)

        # write to file: url, emails
        self.write_to_file(base_url)

        # print
        if self._output:
            print '{0}\t{1}\t{2}'.format(self._nr, len(self._urls), len(self._emails))
        

        # recursion
        for url in self._urls:
            self.do_crawl(url)

        return True


    @timeout(1)
    def get_html(self, base_url):
        data = None
        try:
            data = urllib2.urlopen(base_url)
            return data.read()
        except:
            return False


    def get_urls(self, base_url, html):
        urls = re.findall(r'href="[\'"]?([^\'" >]+)', html)
        urls_unique = []
        for url in urls:
            if not url in urls_unique and url != base_url and not any(word in url for word in self._excluded):
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

        
    def get_page_title(self, html):
        match = re.search(r'<title[^>]*>(.*?)</title>', html)
        try:
            title = match.group(1)
            return title.decode('utf-8')
        except:
            return False


    def get_meta_keywords(self, html):
        try:
            match = re.search('<meta\sname=["\']keywords["\']\scontent=["\'](.*?)["\']\s/>', html)
            return match.group(1).decode('utf-8')
        except:
            return False


    def get_emails(self, html):
        emails = re.findall(r'[\w.]+@[\w.]+', html)
        emails_unique = []
        for email in emails:
            if not email in emails_unique:
                emails_unique.append(email)
        return emails_unique


    def write_to_db(self, base_url, title, keywords):
        db = Database()
        db.db_conn()
        db.insert("""INSERT INTO url (url, title, keywords)
                     VALUES (?, ?, ?)""", 
                     (base_url, title, keywords))


    def write_to_file(self, base_url):
        if not len(self._emails):
            return
        with open(self._filename, 'a') as textfile:
            output = '{0}) {1}:\n'.format(self._nr, base_url)
            # output += 'URLs: (%d)\n' % len(self._urls)
            # output += ', '.join(self._urls)
            output += '\nE-mails: (%d)\n' % len(self._emails)
            output += ', '.join(self._emails) + '\n\n'
            textfile.write(output)


    def main(self):
        if len(sys.argv) > 2:
            url = sys.argv[1]
            self._filename = sys.argv[2]
        elif len(sys.argv) > 1:
            url = sys.argv[1]
        else:
            print 'Use URL and textfile as argument: python pycrawler.py http://www.domain.com filename.txt'
            sys.exit(0)
        print 'Nr.\tURLs\tE-mails'
        self.crawl(url, self._filename, output=True)



if __name__ == '__main__':
    Crawler().main()
