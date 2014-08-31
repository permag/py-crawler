from timeout import Timeout
from db import Database
from bs4 import BeautifulSoup
import re, urllib2
import collections
import sys, os


class Crawler:

    DIR_PATH = os.path.dirname(os.path.abspath(__file__))


    def __init__(self):
        self._emails = []
        self._urls_visited = {}
        self._excluded = ['mailto:', 'favicon', '.ico', '.css', '.js', 
                          '.jpg', '.jpeg', '.png', '.gif', '#', '?', 
                          '.pdf', '.doc']
        self._nr = 0
        self._output = False
        self._filename = '{0}/../data/emails.txt'.format(self.DIR_PATH)
        self._max_depth = 0

        # DB
        self._db = Database()


    @property
    def nr(self):
        return self._nr


    def crawl(self, base_url, filename=None, output=False, search='bfs', max_depth=50):
        # reset
        self._nr = 0
        self._max_depth = max_depth
        self._output = output

        # db conn
        self._db.db_conn()

        # strip url
        base_url = base_url.strip()

        # add http if missing
        if base_url[:7] == 'http://' or base_url[:8] == 'https://':
            pass
        else:
            base_url = 'http://{}'.format(base_url)
        
        # dont crawl same init url twice
        if base_url in self._urls_visited:
            return

        # BFS or DFS
        if search.lower() == 'bfs':
            return self._do_crawl_bfs(base_url)
        elif search.lower() == 'dfs':
            return self._do_crawl_dfs(base_url)


    def _do_crawl_bfs(self, base_url):
        # new queue
        urls_queue = collections.deque()
        # depth
        depth = 0
        # enqueue and visit first url
        self._urls_visited[base_url] = 1
        urls_queue.append(base_url)

        while len(urls_queue):
            if depth > self._max_depth:
                return True
            # dequeue url
            base_url = urls_queue.popleft()
            # check if goto next depth
            if base_url == 'new_depth':
                base_url = urls_queue.popleft()
                depth += 1

            # get html
            html = self._get_html(base_url)
            if not html:
                continue

            # count
            self._nr += 1
            # collect and write data
            self._collect_and_write(base_url, html)
            # get urls
            urls = self._get_urls(base_url, html)

            # print
            if self._output:
                self._print_output(self._nr, len(urls), len(self._emails), depth)

            # enqueue and visit urls
            urls_queue.append('new_depth')
            for url in urls:
                if url not in self._urls_visited:
                    self._urls_visited[url] = 1
                    urls_queue.append(url)

        return True


    def _do_crawl_dfs(self, base_url, depth=0):
        if depth > self._max_depth:
            return
        if base_url in self._urls_visited:
            return
        self._urls_visited[base_url] = 1

        # get html
        html = self._get_html(base_url)
        if not html:
            return

        # count
        self._nr += 1
        # collect and write data
        self._collect_and_write(base_url, html)
        # get urls
        urls = self._get_urls(base_url, html)

        # print
        if self._output:
            self._print_output(self._nr, len(urls), len(self._emails), depth)

        # recursion
        for url in urls:
            self._do_crawl_dfs(url, depth + 1)

        return True


    def _collect_and_write(self, base_url, html):
        # get page title
        title = self._get_page_title(html)
        # get meta keywords
        keywords = self._get_meta_keywords(html)
        # write to db: url, title, keywords, date
        self._write_to_db(base_url, title, keywords)
        # get emails
        self._emails = self._get_emails(html)
        # write to file: url, emails
        self._write_to_file(base_url)


    def _get_html(self, base_url):
        html_content = None
        try:
            with Timeout(seconds=1):
                req = urllib2.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
                html_content = urllib2.urlopen(req).read()
                html = collections.namedtuple('HTML', ['html', 'soup'])
                return html(html_content, BeautifulSoup(html_content, 'lxml'))
        except:
            return False


    def _get_urls(self, base_url, html):
        # urls = re.findall(r'href="[\'"]?([^\'" >]+)', html)
        # urls = [a.get('href') for a in html.soup.find_all('a') if a.get('href') and not any(word in a.get('href') for word in self._excluded)]
        urls_unique = []
        for url in html.soup.find_all('a'):
            url = url.get('href')
            if url and url not in urls_unique and url != base_url and not any(word in url for word in self._excluded):
                if url[:7] == 'http://' or url[:8] == 'https://' or url[:3] == 'www':
                    urls_unique.append(url)
                elif url[:3] == '../':
                    url = url[3:]
                elif url[:2] == './':
                    url = url[2:]
                elif url[0] == '/' or '.':
                    url = url[1:]
                else:                
                    urls_unique.append('{0}{1}'.format(base_url, url))
        return urls_unique


    def _get_page_title(self, html):
        # match = re.search(r'<title[^>]*>(.*?)</title>', html)
        try:
            title = html.soup.title.string   
            # title = match.group(1)
            # return unicode(title)
            return title
        except:
            return False


    def _get_meta_keywords(self, html):
        try:
            match = re.search('<meta\sname=["\']keywords["\']\scontent=["\'](.*?)["\']\s/>', html.html)
            return unicode(match.group(1))
        except:
            return False


    def _get_emails(self, html):
        emails = re.findall(r'[\w.]+@[\w.]+', html.html)
        emails_unique = []
        for email in emails:
            if not email in emails_unique:
                emails_unique.append(email)
        return emails_unique


    def _write_to_db(self, base_url, title, keywords):
        self._db.execute("""INSERT INTO url (url, title, keywords)
                            VALUES (?, ?, ?)""", 
                        (base_url, title, keywords))


    def _write_to_file(self, base_url):
        if not len(self._emails):
            return
        with open(self._filename, 'a') as textfile:
            output = '{0}) {1}:\n'.format(self._nr, base_url)
            # output += 'URLs: (%d)\n' % len(self._urls)
            # output += ', '.join(self._urls)
            output += '\nE-mails: (%d)\n' % len(self._emails)
            output += ', '.join(self._emails) + '\n\n'
            textfile.write(output)


    def _print_output(self, nr, urls_len, emails_len, depth):
            print '{0}\t{1}\t{2}\t{3}'.format(nr, urls_len, emails_len, depth)


    def main(self):
        if len(sys.argv) > 1:
            url = sys.argv[1]
        else:
            print 'Use URL as argument: python pycrawler.py http://www.domain.com'
            sys.exit(0)
        print 'Nr.\tURLs\tE-mails\tDepth'
        self.crawl(url, self._filename, output=True)



if __name__ == '__main__':
    Crawler().main()
