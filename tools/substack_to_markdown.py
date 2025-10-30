#!/usr/bin/env python3
"""
Substack to Markdown Converter

Converts all posts from a Substack publication to individual markdown files.
Handles pagination and preserves post metadata.

Usage:
    python substack_to_markdown.py <substack_url> [--output-dir <dir>]

Example:
    python substack_to_markdown.py https://example.substack.com --output-dir ./posts
"""

import argparse
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
import html2text


class SubstackScraper:
    """Scrapes and converts Substack posts to markdown."""
    
    def __init__(self, base_url: str, output_dir: str = "./substack_posts"):
        """Initialize the scraper with a Substack URL."""
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Parse the domain for the publication name
        parsed = urlparse(base_url)
        self.publication_name = parsed.hostname.split('.')[0]
        
        # Setup HTML to Markdown converter
        self.h2t = html2text.HTML2Text()
        self.h2t.body_width = 0  # No line wrapping
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_emphasis = False
        
        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_archive_posts(self) -> List[Dict]:
        """Fetch all posts from the Substack archive API."""
        posts = []
        offset = 0
        limit = 12  # Substack's default pagination size
        
        print(f"Fetching posts from {self.publication_name}...")
        
        while True:
            # Substack's API endpoint for post archives
            api_url = f"{self.base_url}/api/v1/archive"
            params = {
                'sort': 'new',
                'search': '',
                'offset': offset,
                'limit': limit
            }
            
            try:
                response = self.session.get(api_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data or len(data) == 0:
                    break
                
                posts.extend(data)
                print(f"  Fetched {len(posts)} posts so far...")
                
                # Check if we've reached the end
                if len(data) < limit:
                    break
                
                offset += limit
                time.sleep(1)  # Be polite to the server
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching archive: {e}")
                break
        
        print(f"Total posts found: {len(posts)}")
        return posts
    
    def fetch_post_content(self, post_url: str) -> Optional[str]:
        """Fetch the full content of a single post."""
        try:
            response = self.session.get(post_url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching post {post_url}: {e}")
            return None
    
    def extract_post_content(self, html: str) -> Dict:
        """Extract the main content and metadata from post HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try to find the main article content
        article = soup.find('article')
        if not article:
            # Fallback to looking for common Substack content divs
            article = soup.find('div', class_='post-content')
            if not article:
                article = soup.find('div', class_='body')
        
        # Extract metadata from meta tags
        metadata = {}
        
        # Title
        title_tag = soup.find('meta', property='og:title')
        metadata['title'] = title_tag.get('content', '') if title_tag else ''
        
        # Description
        desc_tag = soup.find('meta', property='og:description')
        metadata['description'] = desc_tag.get('content', '') if desc_tag else ''
        
        # Author
        author_tag = soup.find('meta', attrs={'name': 'author'})
        metadata['author'] = author_tag.get('content', '') if author_tag else ''
        
        # Published date
        date_tag = soup.find('meta', property='article:published_time')
        metadata['date'] = date_tag.get('content', '') if date_tag else ''
        
        # Get the actual content
        content_html = str(article) if article else ''
        
        return {
            'metadata': metadata,
            'content_html': content_html
        }
    
    def convert_to_markdown(self, post_data: Dict, post_url: str) -> str:
        """Convert post data to markdown format with frontmatter."""
        metadata = post_data.get('metadata', {})
        content_html = post_data.get('content_html', '')
        
        # Convert HTML to markdown
        content_md = self.h2t.handle(content_html)
        
        # Clean up the markdown
        content_md = self.clean_markdown(content_md)
        
        # Format date if available
        date_str = metadata.get('date', '')
        if date_str:
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_str = date_obj.strftime('%Y-%m-%d')
            except:
                pass
        
        # Create frontmatter
        frontmatter = [
            '---',
            f'title: "{metadata.get("title", "Untitled")}"',
            f'author: "{metadata.get("author", "Unknown")}"',
            f'date: {date_str}',
            f'url: {post_url}',
            f'description: "{metadata.get("description", "")}"',
            '---',
            ''
        ]
        
        # Combine frontmatter and content
        full_markdown = '\n'.join(frontmatter) + '\n' + content_md
        
        return full_markdown
    
    def clean_markdown(self, markdown: str) -> str:
        """Clean up the converted markdown."""
        # Remove excessive blank lines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        # Fix common conversion issues
        markdown = re.sub(r'!\[\]\(', '![Image](', markdown)  # Fix empty image alt text
        
        # Remove any remaining HTML comments
        markdown = re.sub(r'<!--.*?-->', '', markdown, flags=re.DOTALL)
        
        return markdown.strip()
    
    def create_filename(self, post: Dict) -> str:
        """Create a safe filename from post data."""
        # Try to use slug from URL first
        post_url = post.get('canonical_url', post.get('post_url', ''))
        slug = post_url.split('/')[-1] if post_url else ''
        
        if not slug:
            # Fallback to title
            title = post.get('title', 'untitled')
            slug = re.sub(r'[^\w\s-]', '', title.lower())
            slug = re.sub(r'[-\s]+', '-', slug)
        
        # Add date prefix if available
        date = post.get('post_date')
        if date:
            try:
                date_obj = datetime.fromisoformat(date.replace('Z', '+00:00'))
                date_prefix = date_obj.strftime('%Y-%m-%d')
                filename = f"{date_prefix}-{slug}.md"
            except:
                filename = f"{slug}.md"
        else:
            filename = f"{slug}.md"
        
        return filename
    
    def scrape_and_convert(self):
        """Main method to scrape all posts and convert to markdown."""
        # Method 1: Try the archive API first
        posts = self.get_archive_posts()
        
        if not posts:
            print("No posts found via API. Trying alternative method...")
            posts = self.scrape_archive_page()
        
        if not posts:
            print("No posts found. Please check the URL.")
            return
        
        print(f"\nProcessing {len(posts)} posts...")
        
        for i, post in enumerate(posts, 1):
            # Get the post URL
            post_url = post.get('canonical_url', post.get('post_url', ''))
            if not post_url:
                continue
            
            # Make sure it's a full URL
            if not post_url.startswith('http'):
                post_url = urljoin(self.base_url, post_url)
            
            print(f"\n[{i}/{len(posts)}] Processing: {post.get('title', 'Untitled')}")
            print(f"  URL: {post_url}")
            
            # Fetch the full post content
            html_content = self.fetch_post_content(post_url)
            if not html_content:
                print("  Failed to fetch content, skipping...")
                continue
            
            # Extract content and metadata
            post_data = self.extract_post_content(html_content)
            
            # Convert to markdown
            markdown = self.convert_to_markdown(post_data, post_url)
            
            # Save to file
            filename = self.create_filename(post)
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            print(f"  Saved to: {filepath}")
            
            # Be polite to the server
            time.sleep(2)
        
        print(f"\n✅ Completed! All posts saved to: {self.output_dir}")
    
    def scrape_archive_page(self) -> List[Dict]:
        """Alternative method: Scrape the archive page directly."""
        posts = []
        archive_url = f"{self.base_url}/archive"
        
        print(f"Fetching archive page: {archive_url}")
        
        try:
            response = self.session.get(archive_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for post links
            post_links = soup.find_all('a', class_='post-preview-title')
            if not post_links:
                # Try alternative selectors
                post_links = soup.find_all('a', href=re.compile(r'/p/'))
            
            for link in post_links:
                post = {
                    'title': link.get_text(strip=True),
                    'canonical_url': urljoin(self.base_url, link.get('href', ''))
                }
                posts.append(post)
            
            print(f"Found {len(posts)} posts on archive page")
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching archive page: {e}")
        
        return posts


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Convert Substack posts to Markdown files'
    )
    parser.add_argument(
        'url',
        help='The Substack publication URL (e.g., https://example.substack.com)'
    )
    parser.add_argument(
        '--output-dir',
        default='./substack_posts',
        help='Directory to save markdown files (default: ./substack_posts)'
    )
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith('http'):
        args.url = 'https://' + args.url
    
    # Create scraper and run
    scraper = SubstackScraper(args.url, args.output_dir)
    scraper.scrape_and_convert()


if __name__ == '__main__':
    main()