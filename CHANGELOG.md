## Change Log

### Reddit Content Cleaner v1.1.1
- Added a 'banned_mode' option to the default configuration (set to False initially)
- Modified the process_comment and process_post methods to check for banned_mode before attempting to edit content
- Added a new menu option (#11) to toggle banned mode on/off
- Updated all version references from 1.1.0 to 1.1.1
- Added logging to indicate when banned mode is active during processing
- Updated the menu option numbering (Quit is now option 12)

When banned mode is enabled, the script will skip the edit step and proceed directly to deletion, which will prevent errors when working with a banned account.

### Reddit Content Cleaner v1.1.0
- Added progress bars using the tqdm library to show real-time progress during content removal operations
- Added counters to show the total number of items processed and removed
- Enhanced the user interface with clearer formatting and emojis
- Added item counts at the beginning of operations to give users an estimate of how many items will be processed
- Added a confirmation prompt when removing all posts to prevent accidental deletions
- Added automatic detection and installation prompt for the tqdm library if it's not installed
- Improved the config saving when toggling dry run mode
- Added better summary statistics after operations complete
- Updated version number to reflect the enhancements

### Reddit Content Cleaner v1.0.0 (Patch 042425)
- Fixed all instances of content.sub to use the proper PRAW syntax
- Made all references to self.reddit.user.me() consistent throughout the code

### Reddit Content Cleaner v1.0.0
- All future releases will be now published as "Reddit Content Cleaner" not "RedditCommentCleaner"
- Integrated post clean up
- Added media backup

### RedditCommentCleaner v2.0.0 (alpha)
- Added configuration file support
- Implemented dry run mode
- Added subreddit-specific deletion
- Added keyword-based deletion
- Improved logging and backup system
- Added type hints and better error handling
- Converted to class-based structure

### RedditCommentCleaner v1.9.1
- Added randomized 6-8 second delay between deletions
- API rate limit improvements

### RedditCommentCleaner v1.9
- Moved credentials to external file
- Updated datetime handling for timezone support
