from timeout import Timeout
from db import Database
import re, urllib2
import collections
import sys, os


class Crawler:

    def __init__(self):
        self._urls_queue = collections.deque()
        self._emails = []
        self._urls_visited = []
        self._excluded = ['favicon', '.ico', '.css', '.js', '.jpg', 
                         '.jpeg', '.png', '.gif', '#', '?', '.pdf',
                         '.doc']
        self._nr = 0
        self._output = False
        self._filename = 'emails.txt'


    @property
    def nr(self):
        return self._nr


    def crawl(self, base_url, filename=None, output=False, search='bfs'):
        base_url = base_url.strip()
        if base_url[:7] == 'http://' or base_url[:8] == 'https://':
            pass
        else:
            base_url = 'http://{}'.format(base_url)

        self._nr = 0
        if output:
            self._output = True

        if search.lower() == 'bfs':
            return self.do_crawl_bfs(base_url)
        elif search.lower() == 'dfs':
            return self.do_crawl_dfs(base_url)


    def do_crawl_bfs(self, base_url):
        # enqueue first url
        self._urls_queue.append(base_url)

        while len(self._urls_queue):
            # dequeue url
            base_url = self._urls_queue.popleft()

            if base_url in self._urls_visited:
                continue
            self._urls_visited.append(base_url)

            # get html
            html = self.get_html(base_url)
            if not html:
                continue
            
            # count
            self._nr += 1
            
            # collect and write data
            self.collect_and_write(base_url, html)

            # get urls
            urls = self.get_urls(base_url, html)

            # print
            if self._output:
                print '{0}\t{1}\t{2}'.format(self._nr, len(urls), len(self._emails))

            # enqueue list of urls into queue
            self._urls_queue += urls

        return True


    def do_crawl_dfs(self, base_url, level=0):
        # if level > 7:
        #     return
        if base_url in self._urls_visited:
            return
        self._urls_visited.append(base_url)

        # get html
        html = self.get_html(base_url)
        if not html:
            return

        # count
        self._nr += 1

        # collect and write data
        self.collect_and_write(base_url, html)

        # get urls
        urls = self.get_urls(base_url, html)

        # print
        if self._output:
            print '{0}\t{1}\t{2}\t{3}'.format(self._nr, len(urls), len(self._emails), level)

        # recursion
        for url in urls:
            self.do_crawl_dfs(url, level + 1)

        return True


    def collect_and_write(self, base_url, html):
        # get page title
        title = self.get_page_title(html)
        # get meta keywords
        keywords = self.get_meta_keywords(html)
        # get emails
        self._emails = self.get_emails(html)
        # write to db: url, title, keywords, date
        self.write_to_db(base_url, title, keywords)
        # write to file: url, emails
        self.write_to_file(base_url)


    def get_html(self, base_url):
        html = None
        try:
            with Timeout(seconds=1):
                req = urllib2.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
                html = urllib2.urlopen(req).read()
                return html
        except:
            return False


    def get_urls(self, base_url, html):
        urls = re.findall(r'href="[\'"]?([^\'" >]+)', html)
        urls_unique = []
        for url in urls:
            if not url in urls_unique and url != base_url and not any(word in url for word in self._excluded):
                if url[:7] == 'http://' or url[:8] == 'https://' or url[:3] == 'www':
                    urls_unique.append(url)
                elif len(url) > 200:
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
