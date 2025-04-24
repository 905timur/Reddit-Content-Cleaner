import praw
import datetime
import pytz
import random
import time
import logging
from typing import Optional, List, Dict
import json
import re
import os
import requests
from urllib.parse import urlparse

class RedditContentCleaner:
    def __init__(self, credentials_file: str = "credentials.txt"):
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('content_cleaner.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Create media directory if it doesn't exist
        self.media_dir = 'post_media'
        os.makedirs(self.media_dir, exist_ok=True)

        # Initialize Reddit instance
        self.credentials = self._load_credentials(credentials_file)
        self.reddit = praw.Reddit(
            client_id=self.credentials['client_id'],
            client_secret=self.credentials['client_secret'],
            username=self.credentials['username'],
            password=self.credentials['password'],
            user_agent="Content Cleaner v3.0"
        )

        # Load configuration
        self.config = self._load_config()

    def _load_credentials(self, file_path: str) -> Dict[str, str]:
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            return {
                'client_id': lines[0].strip(),
                'client_secret': lines[1].strip(),
                'username': lines[2].strip(),
                'password': lines[3].strip()
            }
        except Exception as e:
            self.logger.error(f"Error loading credentials: {str(e)}")
            raise

    def _load_config(self) -> Dict:
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            config = {
                'replacement_text': ".",
                'min_delay': 6,
                'max_delay': 8,
                'excluded_subs': [],
                'excluded_keywords': [],
                'backup_enabled': True,
                'dry_run': False
            }
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            return config

    def backup_content(self, content, content_type: str) -> None:
        if self.config['backup_enabled']:
            with open('deleted_content.txt', 'a', encoding='utf-8') as f:
                f.write(f"Type: {content_type}\n")
                f.write(f"Timestamp: {datetime.datetime.now(pytz.UTC)}\n")
                f.write(f"Score: {content.score}\n")
                f.write(f"Sub: {content.subreddit.display_name}\n")
                if content_type == "post":
                    f.write(f"Title: {content.title}\n")
                    if hasattr(content, 'selftext'):
                        f.write(f"Content: {content.selftext}\n")
                    if hasattr(content, 'url'):
                        f.write(f"URL: {content.url}\n")
                else:
                    f.write(f"Content: {content.body}\n")
                f.write("-" * 50 + "\n")

    def download_media(self, post) -> None:
        try:
            url = post.url.lower()
            if any(url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4']):
                filename = os.path.join(self.media_dir, os.path.basename(urlparse(url).path))
                response = requests.get(url, stream=True)
                response.raise_for_status()

                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.logger.info(f"Downloaded media: {filename}")
        except Exception as e:
            self.logger.error(f"Error downloading media: {str(e)}")

    def should_exclude_content(self, content) -> bool:
        if str(content.subreddit.display_name) in self.config['excluded_subs']:
            return True

        content_text = content.selftext if hasattr(content, 'selftext') else content.body
        for keyword in self.config['excluded_keywords']:
            if keyword.lower() in content_text.lower():
                return True

        return False

    def process_comment(self, comment) -> None:
        if not self.should_exclude_content(comment):
            try:
                self.backup_content(comment, "comment")
                if not self.config['dry_run']:
                    comment.edit(self.config['replacement_text'])
                    comment.delete()
                    delay = random.uniform(self.config['min_delay'], self.config['max_delay'])
                    time.sleep(delay)
                self.logger.info(f"Processed comment in r/{comment.subreddit.display_name}")
            except Exception as e:
                self.logger.error(f"Error processing comment: {str(e)}")

    def process_post(self, post) -> None:
        if not self.should_exclude_content(post):
            try:
                self.backup_content(post, "post")

                # Download media if present
                if hasattr(post, 'url'):
                    self.download_media(post)

                if not self.config['dry_run']:
                    # Edit if it's a text post
                    if hasattr(post, 'selftext') and post.selftext:
                        post.edit(self.config['replacement_text'])

                    post.delete()
                    delay = random.uniform(self.config['min_delay'], self.config['max_delay'])
                    time.sleep(delay)
                self.logger.info(f"Processed post in r/{post.subreddit.display_name}")
            except Exception as e:
                self.logger.error(f"Error processing post: {str(e)}")

    # Existing comment methods...
    def remove_old_comments(self, days: int) -> None:
        cutoff = datetime.datetime.now(pytz.UTC) - datetime.timedelta(days=days)
        for comment in self.reddit.user.me().comments.new(limit=None):
            comment_time = datetime.datetime.fromtimestamp(comment.created_utc, pytz.UTC)
            if comment_time < cutoff:
                self.process_comment(comment)

    def remove_negative_karma(self) -> None:
        for comment in self.reddit.user.me().comments.new(limit=None):
            if comment.score < 0:
                self.process_comment(comment)

    def remove_low_engagement(self) -> None:
        for comment in self.reddit.user.me().comments.new(limit=None):
            if comment.score <= 1 and len(comment.replies) == 0:
                self.process_comment(comment)

    # New post methods
    def remove_all_posts(self) -> None:
        for post in self.reddit.user.me().submissions.new(limit=None):
            self.process_post(post)

    def remove_old_posts(self, days: int) -> None:
        cutoff = datetime.datetime.now(pytz.UTC) - datetime.timedelta(days=days)
        for post in self.reddit.user.me().submissions.new(limit=None):
            post_time = datetime.datetime.fromtimestamp(post.created_utc, pytz.UTC)
            if post_time < cutoff:
                self.process_post(post)

    def remove_low_karma_posts(self, threshold: int) -> None:
        for post in self.reddit.user.me().submissions.new(limit=None):
            if post.score < threshold:
                self.process_post(post)

    # Existing methods for subreddit and keyword...
    def remove_by_subreddit(self, subreddit_name: str) -> None:
        for comment in self.reddit.user.me().comments.new(limit=None):
            if str(comment.subreddit.display_name).lower() == subreddit_name.lower():
                self.process_comment(comment)
        for post in self.reddit.user.me().submissions.new(limit=None):
            if str(post.subreddit.display_name).lower() == subreddit_name.lower():
                self.process_post(post)

    def remove_by_keyword(self, keyword: str) -> None:
        for comment in self.reddit.user.me().comments.new(limit=None):
            if keyword.lower() in comment.body.lower():
                self.process_comment(comment)
        for post in self.reddit.user.me().submissions.new(limit=None):
            if keyword.lower() in post.title.lower() or (hasattr(post, 'selftext') and keyword.lower() in post.selftext.lower()):
                self.process_post(post)

def main():
    cleaner = RedditContentCleaner()

    while True:
        print("\nReddit Content Cleaner v1.0.0")
        print("\nComment Options:")
        print("1. Remove comments older than x days")
        print("2. Remove comments with negative karma")
        print("3. Remove comments with 1 karma and no replies")
        print("\nPost Options:")
        print("4. Remove all posts")
        print("5. Remove posts older than x days")
        print("6. Remove posts under x upvotes")
        print("\nGeneral Options:")
        print("7. Remove content from specific subreddit")
        print("8. Remove content containing keyword")
        print("9. Edit configuration")
        print("10. Enable/Disable dry run")
        print("11. Quit")

        choice = input("\nEnter your choice (1-11): ")

        try:
            if choice == "1":
                days = int(input("Enter number of days: "))
                cleaner.remove_old_comments(days)
            elif choice == "2":
                cleaner.remove_negative_karma()
            elif choice == "3":
                cleaner.remove_low_engagement()
            elif choice == "4":
                cleaner.remove_all_posts()
            elif choice == "5":
                days = int(input("Enter number of days: "))
                cleaner.remove_old_posts(days)
            elif choice == "6":
                threshold = int(input("Enter upvote threshold: "))
                cleaner.remove_low_karma_posts(threshold)
            elif choice == "7":
                subreddit = input("Enter subreddit name: ")
                cleaner.remove_by_subreddit(subreddit)
            elif choice == "8":
                keyword = input("Enter keyword: ")
                cleaner.remove_by_keyword(keyword)
            elif choice == "9":
                print("\nCurrent configuration:")
                print(json.dumps(cleaner.config, indent=4))
                print("\nEdit config.json file to make changes")
            elif choice == "10":
                cleaner.config['dry_run'] = not cleaner.config['dry_run']
                print(f"Dry run {'enabled' if cleaner.config['dry_run'] else 'disabled'}")
            elif choice == "11":
                break
        except ValueError as e:
            print(f"Invalid input: {str(e)}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
