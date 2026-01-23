#!/usr/bin/env python3
"""
Spider Entity Deployment System
A web crawling and data extraction system integrated with Hybrid VCS
"""

import asyncio
import aiohttp
import json
import sqlite3
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
import logging
from dataclasses import dataclass
import argparse

@dataclass
class SpiderConfig:
    """Configuration for spider entity"""
    start_urls: List[str]
    max_depth: int = 3
    max_pages: int = 1000
    delay: float = 1.0
    user_agent: str = "SpiderEntity/1.0 (Hybrid VCS)"
    respect_robots: bool = True
    allowed_domains: Set[str] = None
    
    def __post_init__(self):
        if self.allowed_domains is None:
            self.allowed_domains = {urlparse(url).netloc for url in self.start_urls}

class SpiderEntity:
    """Web crawling entity with VCS integration"""
    
    def __init__(self, config: SpiderConfig, db_path: str = "spider_data.db"):
        self.config = config
        self.db_path = db_path
        self.visited_urls: Set[str] = set()
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = self._setup_logger()
        self._init_database()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for spider entity"""
        logger = logging.getLogger('spider_entity')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def _init_database(self):
        """Initialize SQLite database for storing crawled data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                content_hash TEXT,
                content_length INTEGER,
                status_code INTEGER,
                crawl_time TIMESTAMP,
                depth INTEGER,
                parent_url TEXT,
                links_found TEXT,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawl_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                pages_crawled INTEGER,
                config TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={'User-Agent': self.config.user_agent},
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    def _get_url_hash(self, url: str) -> str:
        """Generate hash for URL to track uniqueness"""
        return hashlib.md5(url.encode()).hexdigest()
        
    async def fetch_page(self, url: str) -> Optional[Dict]:
        """Fetch a single page"""
        try:
            async with self.session.get(url) as response:
                content = await response.text()
                return {
                    'url': url,
                    'status_code': response.status,
                    'content': content,
                    'headers': dict(response.headers)
                }
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
            
    def extract_links(self, content: str, base_url: str) -> List[str]:
        """Extract links from HTML content"""
        import re
        links = []
        
        # Simple regex for href extraction
        href_pattern = r'href=["\']([^"\']+)["\']'
        matches = re.findall(href_pattern, content, re.IGNORECASE)
        
        for match in matches:
            absolute_url = urljoin(base_url, match)
            parsed = urlparse(absolute_url)
            
            # Only include HTTP/HTTPS URLs from allowed domains
            if (parsed.scheme in ['http', 'https'] and 
                parsed.netloc in self.config.allowed_domains):
                links.append(absolute_url)
                
        return links
        
    def extract_title(self, content: str) -> str:
        """Extract page title from HTML"""
        import re
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        return title_match.group(1).strip() if title_match else "No Title"
        
    async def crawl_page(self, url: str, depth: int = 0) -> List[str]:
        """Crawl a single page and return discovered links"""
        if depth > self.config.max_depth or len(self.visited_urls) >= self.config.max_pages:
            return []
            
        url_hash = self._get_url_hash(url)
        if url_hash in self.visited_urls:
            return []
            
        self.visited_urls.add(url_hash)
        self.logger.info(f"Crawling: {url} (depth: {depth})")
        
        page_data = await self.fetch_page(url)
        if not page_data:
            return []
            
        # Extract metadata
        title = self.extract_title(page_data['content'])
        links = self.extract_links(page_data['content'], url)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO pages 
            (url, title, content_hash, content_length, status_code, crawl_time, depth, links_found)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            url,
            title,
            self._get_url_hash(page_data['content']),
            len(page_data['content']),
            page_data['status_code'],
            datetime.now(),
            depth,
            json.dumps(links)
        ))
        
        conn.commit()
        conn.close()
        
        # Respect crawl delay
        await asyncio.sleep(self.config.delay)
        
        return links
        
    async def crawl(self) -> Dict:
        """Start crawling process"""
        start_time = datetime.now()
        pages_crawled = 0
        
        # Record crawl session
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO crawl_sessions (start_time, config) VALUES (?, ?)
        ''', (start_time, json.dumps(self.config.__dict__)))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # BFS crawling
        queue = [(url, 0) for url in self.config.start_urls]
        
        while queue and len(self.visited_urls) < self.config.max_pages:
            current_batch = queue[:10]  # Process 10 URLs at a time
            queue = queue[10:]
            
            tasks = []
            for url, depth in current_batch:
                if depth <= self.config.max_depth:
                    tasks.append(self.crawl_page(url, depth))
                    
            results = await asyncio.gather(*tasks)
            
            for links in results:
                if links:
                    for link in links:
                        if self._get_url_hash(link) not in self.visited_urls:
                            queue.append((link, depth + 1))
                            
            pages_crawled += len(current_batch)
            
        # Update crawl session
        end_time = datetime.now()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE crawl_sessions 
            SET end_time = ?, pages_crawled = ? 
            WHERE id = ?
        ''', (end_time, pages_crawled, session_id))
        conn.commit()
        conn.close()
        
        return {
            'pages_crawled': pages_crawled,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'total_time': str(end_time - start_time)
        }
        
    def get_crawl_stats(self) -> Dict:
        """Get statistics about crawled data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM pages')
        total_pages = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT depth) FROM pages')
        max_depth = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(content_length) FROM pages')
        avg_content_length = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_pages': total_pages,
            'max_depth_reached': max_depth,
            'average_content_length': int(avg_content_length)
        }

async def main():
    """Main entry point for spider entity deployment"""
    parser = argparse.ArgumentParser(description='Spider Entity Deployment System')
    parser.add_argument('urls', nargs='+', help='Starting URLs to crawl')
    parser.add_argument('--max-depth', type=int, default=3, help='Maximum crawl depth')
    parser.add_argument('--max-pages', type=int, default=1000, help='Maximum pages to crawl')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests')
    parser.add_argument('--db-path', default='spider_data.db', help='Database file path')
    
    args = parser.parse_args()
    
    config = SpiderConfig(
        start_urls=args.urls,
        max_depth=args.max_depth,
        max_pages=args.max_pages,
        delay=args.delay
    )
    
    async with SpiderEntity(config, args.db_path) as spider:
        results = await spider.crawl()
        stats = spider.get_crawl_stats()
        
        print("Spider Entity Deployment Complete!")
        print(f"Pages crawled: {results['pages_crawled']}")
        print(f"Total time: {results['total_time']}")
        print(f"Database: {args.db_path}")
        print(f"Total pages in DB: {stats['total_pages']}")

if __name__ == "__main__":
    asyncio.run(main())
