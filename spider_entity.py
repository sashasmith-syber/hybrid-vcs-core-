"""
Spider Entity - Web Crawler with VCS Integration
Automatically crawls web pages and version-controls the content
"""

import json
import time
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from hybrid_vcs_original import HybridVCS


class SpiderEntity:
    """
    Web crawler that integrates with Hybrid VCS
    
    Features:
    - Configurable crawl depth and URL patterns
    - Content change detection
    - Automatic version control of crawled pages
    - Support for webpage snapshots
    """
    
    def __init__(self, config_path: str = "spider_config.json", vcs_repo: str = "spider-data"):
        """
        Initialize Spider Entity
        
        Args:
            config_path: Path to configuration file
            vcs_repo: Repository name for storing crawled data
        """
        self.config = self._load_config(config_path)
        self.vcs = HybridVCS()
        self.vcs_repo = vcs_repo
        self.crawl_cache = {}
        self.stats = {
            "pages_crawled": 0,
            "pages_changed": 0,
            "pages_new": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }
        
        # Initialize VCS repository if it doesn't exist
        repos = self.vcs.list_repositories()
        if not any(r['name'] == vcs_repo for r in repos):
            self.vcs.init_repository(vcs_repo)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load spider configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            return {
                "max_depth": 2,
                "max_pages": 50,
                "delay_seconds": 1,
                "user_agent": "HybridVCS-Spider/1.0",
                "allowed_domains": [],
                "url_patterns": [],
                "exclude_patterns": [],
                "follow_external": False,
                "timeout": 30
            }
    
    def _compute_content_hash(self, content: str) -> str:
        """Compute hash of page content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _is_allowed_url(self, url: str) -> bool:
        """Check if URL is allowed by configuration"""
        parsed = urlparse(url)
        
        # Check allowed domains
        if self.config.get('allowed_domains'):
            if not any(domain in parsed.netloc for domain in self.config['allowed_domains']):
                return False
        
        # Check URL patterns
        if self.config.get('url_patterns'):
            if not any(pattern in url for pattern in self.config['url_patterns']):
                return False
        
        # Check exclude patterns
        if self.config.get('exclude_patterns'):
            if any(pattern in url for pattern in self.config['exclude_patterns']):
                return False
        
        return True
    
    def fetch_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a web page and extract content
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with page data or None on error
        """
        try:
            headers = {
                'User-Agent': self.config.get('user_agent', 'HybridVCS-Spider/1.0')
            }
            
            response = requests.get(
                url,
                headers=headers,
                timeout=self.config.get('timeout', 30)
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract metadata
            title = soup.title.string if soup.title else url
            
            # Extract text content
            text_content = soup.get_text(separator=' ', strip=True)
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(url, link['href'])
                if self._is_allowed_url(absolute_url):
                    links.append(absolute_url)
            
            page_data = {
                "url": url,
                "title": title,
                "content": response.text,
                "text_content": text_content,
                "links": links,
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', ''),
                "fetched_at": datetime.now().isoformat(),
                "content_hash": self._compute_content_hash(response.text)
            }
            
            return page_data
        
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            self.stats['errors'] += 1
            return None
    
    def save_page(self, page_data: Dict[str, Any]) -> bool:
        """
        Save page data to VCS
        
        Args:
            page_data: Page data dictionary
            
        Returns:
            True if saved successfully
        """
        try:
            # Generate filename from URL
            url_hash = hashlib.md5(page_data['url'].encode()).hexdigest()
            filename = f"page_{url_hash}.json"
            
            # Check if content changed
            changed = True
            if url_hash in self.crawl_cache:
                cached_hash = self.crawl_cache[url_hash]
                if cached_hash == page_data['content_hash']:
                    changed = False
            else:
                self.stats['pages_new'] += 1
            
            if changed:
                # Save to VCS
                content = json.dumps(page_data, indent=2).encode('utf-8')
                self.vcs.add_file(self.vcs_repo, filename, content)
                self.crawl_cache[url_hash] = page_data['content_hash']
                
                if url_hash in [k for k, v in self.crawl_cache.items() if k != url_hash]:
                    self.stats['pages_changed'] += 1
                
                return True
            
            return False
        
        except Exception as e:
            print(f"Error saving page {page_data['url']}: {str(e)}")
            return False
    
    def crawl(self, start_url: str, max_depth: Optional[int] = None) -> Dict[str, Any]:
        """
        Crawl web pages starting from a URL
        
        Args:
            start_url: Starting URL
            max_depth: Maximum crawl depth (overrides config)
            
        Returns:
            Crawl statistics
        """
        self.stats['start_time'] = datetime.now().isoformat()
        
        max_depth = max_depth or self.config.get('max_depth', 2)
        max_pages = self.config.get('max_pages', 50)
        delay = self.config.get('delay_seconds', 1)
        
        to_visit = [(start_url, 0)]  # (url, depth)
        visited = set()
        pages_with_changes = []
        
        print(f"Starting crawl from: {start_url}")
        print(f"Max depth: {max_depth}, Max pages: {max_pages}")
        
        while to_visit and self.stats['pages_crawled'] < max_pages:
            url, depth = to_visit.pop(0)
            
            if url in visited or depth > max_depth:
                continue
            
            visited.add(url)
            
            print(f"Crawling [{depth}/{max_depth}]: {url}")
            
            # Fetch page
            page_data = self.fetch_page(url)
            if not page_data:
                continue
            
            self.stats['pages_crawled'] += 1
            
            # Save to VCS
            if self.save_page(page_data):
                pages_with_changes.append(url)
            
            # Add links to visit queue
            if depth < max_depth:
                for link in page_data.get('links', []):
                    if link not in visited:
                        to_visit.append((link, depth + 1))
            
            # Rate limiting
            time.sleep(delay)
        
        # Commit changes if any
        if pages_with_changes:
            commit_msg = f"Spider crawl: {len(pages_with_changes)} pages updated from {start_url}"
            self.vcs.commit(self.vcs_repo, commit_msg, "Spider Entity")
            print(f"\nCommitted {len(pages_with_changes)} page(s) to VCS")
        
        self.stats['end_time'] = datetime.now().isoformat()
        
        return {
            "success": True,
            "statistics": self.stats,
            "pages_with_changes": pages_with_changes
        }
    
    def get_crawl_history(self) -> Dict[str, Any]:
        """Get crawl history from VCS"""
        return self.vcs.get_history(self.vcs_repo)
    
    def get_page_versions(self, url: str) -> List[Dict[str, Any]]:
        """Get all versions of a specific page"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        filename = f"page_{url_hash}.json"
        
        # Get commits that modified this file
        history = self.vcs.get_history(self.vcs_repo, limit=100)
        versions = []
        
        for commit in history.get('commits', []):
            if filename in commit.get('files', {}):
                versions.append({
                    "commit_id": commit['id'],
                    "timestamp": commit['timestamp'],
                    "message": commit['message']
                })
        
        return versions


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Spider Entity Web Crawler')
    parser.add_argument('url', help='Starting URL to crawl')
    parser.add_argument('--config', default='spider_config.json', help='Config file path')
    parser.add_argument('--repo', default='spider-data', help='VCS repository name')
    parser.add_argument('--depth', type=int, help='Maximum crawl depth')
    
    args = parser.parse_args()
    
    spider = SpiderEntity(config_path=args.config, vcs_repo=args.repo)
    result = spider.crawl(args.url, max_depth=args.depth)
    
    print("\n" + "="*60)
    print("Crawl Complete!")
    print("="*60)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
