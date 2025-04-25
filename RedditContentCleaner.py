import praw
import datetime
import pytz
import random
import time
import logging
from typing import Optional, List, Dict, Iterator
import json
import re
import os
import requests
from urllib.parse import urlparse
from tqdm import tqdm

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
            user_agent="Content Cleaner v1.1.0"
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

    def _count_items(self, iterator: Iterator) -> int:
        """Count the total number of items in an iterator (consumes the iterator)"""
        count = 0
        for _ in iterator:
            count += 1
        return count

    def _get_comment_count(self) -> int:
        """Get an approximate count of user's comments"""
        try:
            return self._count_items(self.reddit.user.me().comments.new(limit=None))
        except Exception as e:
            self.logger.error(f"Error counting comments: {str(e)}")
            return 0

    def _get_post_count(self) -> int:
        """Get an approximate count of user's posts"""
        try:
            return self._count_items(self.reddit.user.me().submissions.new(limit=None))
        except Exception as e:
            self.logger.error(f"Error counting posts: {str(e)}")
            return 0

    def process_comment(self, comment, progress_bar=None) -> None:
        if not self.should_exclude_content(comment):
            try:
                self.backup_content(comment, "comment")
                if not self.config['dry_run']:
                    comment.edit(self.config['replacement_text'])
                    comment.delete()
                    delay = random.uniform(self.config['min_delay'], self.config['max_delay'])
                    time.sleep(delay)
                self.logger.info(f"Processed comment in r/{comment.subreddit.display_name}")
                if progress_bar:
                    progress_bar.update(1)
            except Exception as e:
                self.logger.error(f"Error processing comment: {str(e)}")
                if progress_bar:
                    progress_bar.update(1)

    def process_post(self, post, progress_bar=None) -> None:
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
                if progress_bar:
                    progress_bar.update(1)
            except Exception as e:
                self.logger.error(f"Error processing post: {str(e)}")
                if progress_bar:
                    progress_bar.update(1)

    def remove_old_comments(self, days: int) -> None:
        cutoff = datetime.datetime.now(pytz.UTC) - datetime.timedelta(days=days)

        # First count approximately how many comments we'll process
        print("Estimating comment count...")
        total_comments = self._get_comment_count()
        processed = 0

        print(f"Processing approximately {total_comments} comments...")
        with tqdm(total=total_comments, desc="Removing old comments", unit="comment") as pbar:
            for comment in self.reddit.user.me().comments.new(limit=None):
                comment_time = datetime.datetime.fromtimestamp(comment.created_utc, pytz.UTC)
                if comment_time < cutoff:
                    self.process_comment(comment, pbar)
                else:
                    pbar.update(1)
                processed += 1

        print(f"Completed! Processed {processed} comments.")

    def remove_negative_karma(self) -> None:
        # First count approximately how many comments we'll process
        print("Estimating comment count...")
        total_comments = self._get_comment_count()
        processed = 0
        removed = 0

        print(f"Processing approximately {total_comments} comments...")
        with tqdm(total=total_comments, desc="Removing negative karma comments", unit="comment") as pbar:
            for comment in self.reddit.user.me().comments.new(limit=None):
                if comment.score < 0:
                    self.process_comment(comment, pbar)
                    removed += 1
                else:
                    pbar.update(1)
                processed += 1

        print(f"Completed! Processed {processed} comments, removed {removed} comments.")

    def remove_low_engagement(self) -> None:
        # First count approximately how many comments we'll process
        print("Estimating comment count...")
        total_comments = self._get_comment_count()
        processed = 0
        removed = 0

        print(f"Processing approximately {total_comments} comments...")
        with tqdm(total=total_comments, desc="Removing low engagement comments", unit="comment") as pbar:
            for comment in self.reddit.user.me().comments.new(limit=None):
                if comment.score <= 1 and len(comment.replies) == 0:
                    self.process_comment(comment, pbar)
                    removed += 1
                else:
                    pbar.update(1)
                processed += 1

        print(f"Completed! Processed {processed} comments, removed {removed} comments.")

    def remove_all_posts(self) -> None:
        # First count approximately how many posts we'll process
        print("Estimating post count...")
        total_posts = self._get_post_count()
        processed = 0

        print(f"Processing approximately {total_posts} posts...")
        with tqdm(total=total_posts, desc="Removing all posts", unit="post") as pbar:
            for post in self.reddit.user.me().submissions.new(limit=None):
                self.process_post(post, pbar)
                processed += 1

        print(f"Completed! Removed {processed} posts.")

    def remove_old_posts(self, days: int) -> None:
        cutoff = datetime.datetime.now(pytz.UTC) - datetime.timedelta(days=days)

        # First count approximately how many posts we'll process
        print("Estimating post count...")
        total_posts = self._get_post_count()
        processed = 0
        removed = 0

        print(f"Processing approximately {total_posts} posts...")
        with tqdm(total=total_posts, desc="Removing old posts", unit="post") as pbar:
            for post in self.reddit.user.me().submissions.new(limit=None):
                post_time = datetime.datetime.fromtimestamp(post.created_utc, pytz.UTC)
                if post_time < cutoff:
                    self.process_post(post, pbar)
                    removed += 1
                else:
                    pbar.update(1)
                processed += 1

        print(f"Completed! Processed {processed} posts, removed {removed} posts.")

    def remove_low_karma_posts(self, threshold: int) -> None:
        # First count approximately how many posts we'll process
        print("Estimating post count...")
        total_posts = self._get_post_count()
        processed = 0
        removed = 0

        print(f"Processing approximately {total_posts} posts...")
        with tqdm(total=total_posts, desc="Removing low karma posts", unit="post") as pbar:
            for post in self.reddit.user.me().submissions.new(limit=None):
                if post.score < threshold:
                    self.process_post(post, pbar)
                    removed += 1
                else:
                    pbar.update(1)
                processed += 1

        print(f"Completed! Processed {processed} posts, removed {removed} posts.")

    def remove_by_subreddit(self, subreddit_name: str) -> None:
        # First count approximately how many items we'll process
        print("Estimating content count...")
        total_comments = self._get_comment_count()
        total_posts = self._get_post_count()
        total_items = total_comments + total_posts
        processed_comments = 0
        processed_posts = 0
        removed_comments = 0
        removed_posts = 0

        print(f"Processing approximately {total_items} items...")
        with tqdm(total=total_items, desc=f"Removing content from r/{subreddit_name}", unit="item") as pbar:
            # Process comments first
            for comment in self.reddit.user.me().comments.new(limit=None):
                if str(comment.subreddit.display_name).lower() == subreddit_name.lower():
                    self.process_comment(comment, pbar)
                    removed_comments += 1
                else:
                    pbar.update(1)
                processed_comments += 1

            # Then process posts
            for post in self.reddit.user.me().submissions.new(limit=None):
                if str(post.subreddit.display_name).lower() == subreddit_name.lower():
                    self.process_post(post, pbar)
                    removed_posts += 1
                else:
                    pbar.update(1)
                processed_posts += 1

        print(f"Completed! Processed {processed_comments} comments and {processed_posts} posts.")
        print(f"Removed {removed_comments} comments and {removed_posts} posts from r/{subreddit_name}.")

    def remove_by_keyword(self, keyword: str) -> None:
        # First count approximately how many items we'll process
        print("Estimating content count...")
        total_comments = self._get_comment_count()
        total_posts = self._get_post_count()
        total_items = total_comments + total_posts
        processed_comments = 0
        processed_posts = 0
        removed_comments = 0
        removed_posts = 0

        print(f"Processing approximately {total_items} items...")
        with tqdm(total=total_items, desc=f"Removing content with keyword '{keyword}'", unit="item") as pbar:
            # Process comments first
            for comment in self.reddit.user.me().comments.new(limit=None):
                if keyword.lower() in comment.body.lower():
                    self.process_comment(comment, pbar)
                    removed_comments += 1
                else:
                    pbar.update(1)
                processed_comments += 1

            # Then process posts
            for post in self.reddit.user.me().submissions.new(limit=None):
                if keyword.lower() in post.title.lower() or (hasattr(post, 'selftext') and keyword.lower() in post.selftext.lower()):
                    self.process_post(post, pbar)
                    removed_posts += 1
                else:
                    pbar.update(1)
                processed_posts += 1

        print(f"Completed! Processed {processed_comments} comments and {processed_posts} posts.")
        print(f"Removed {removed_comments} comments and {removed_posts} posts containing '{keyword}'.")

def main():
    cleaner = RedditContentCleaner()

    # Check if tqdm is installed, if not provide installation instructions
    try:
        import tqdm
    except ImportError:
        print("The 'tqdm' package is required for progress bars.")
        print("Please install it using: pip install tqdm")
        install = input("Would you like to install it now? (y/n): ")
        if install.lower() == 'y':
            import subprocess
            subprocess.check_call(["pip", "install", "tqdm"])
            print("tqdm installed successfully!")
        else:
            print("Please install tqdm manually and restart the program.")
            return

    while True:
        print("\n" + "=" * 50)
        print("     Reddit Content Cleaner v1.1.0")
        print("=" * 50)

        print("\n📜 Comment Options:")
        print("  1. Remove comments older than x days")
        print("  2. Remove comments with negative karma")
        print("  3. Remove comments with 1 karma and no replies")

        print("\n📝 Post Options:")
        print("  4. Remove all posts")
        print("  5. Remove posts older than x days")
        print("  6. Remove posts under x upvotes")

        print("\n⚙️ General Options:")
        print("  7. Remove content from specific subreddit")
        print("  8. Remove content containing keyword")
        print("  9. Edit configuration")
        print(" 10. Enable/Disable dry run")
        print(" 11. Quit")

        choice = input("\n👉 Enter your choice (1-11): ")

        try:
            if choice == "1":
                days = int(input("Enter number of days: "))
                cleaner.remove_old_comments(days)
            elif choice == "2":
                cleaner.remove_negative_karma()
            elif choice == "3":
                cleaner.remove_low_engagement()
            elif choice == "4":
                confirm = input("Are you sure you want to remove ALL posts? (y/n): ")
                if confirm.lower() == 'y':
                    cleaner.remove_all_posts()
                else:
                    print("Operation cancelled.")
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
                input("Press Enter to continue...")
            elif choice == "10":
                cleaner.config['dry_run'] = not cleaner.config['dry_run']
                status = "ENABLED" if cleaner.config['dry_run'] else "DISABLED"
                print(f"Dry run {status}")
                # Save the updated config
                with open('config.json', 'w') as f:
                    json.dump(cleaner.config, f, indent=4)
            elif choice == "11":
                print("Thank you for using Reddit Content Cleaner!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 11.")
        except ValueError as e:
            print(f"Invalid input: {str(e)}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
