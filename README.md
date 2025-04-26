![Reddti Content Cleaner](rcc.svg)


# Reddit Content Cleaner v1.1.0
A Python script that helps you manage your Reddit content history by providing various options to clean, edit, and delete posts and comments based on different criteria. The script includes features like age-based deletion, karma-based filtering, and keyword-based management.

## Star History

<p align="center">
  <a href="https://www.star-history.com/#905timur/Reddit-Content-Cleaner&Date">
   <picture>
     <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=905timur/Reddit-Content-Cleaner&type=Date&theme=dark" />
     <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=905timur/Reddit-Content-Cleaner&type=Date" />
     <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=905timur/Reddit-Content-Cleaner&type=Date" />
   </picture>
  </a>
</p>

## Features

### Core Functionality
- Delete posts and comments older than a specified number of days
- Remove comments with negative karma
- Clean up low-engagement comments (1 karma and no replies)
- Target specific subreddits for content cleanup
- Remove content containing specific keywords
- Dry run mode for testing changes before execution
- Configurable comment replacement text
- Detailed logging and backup system

### Safety Features
- Excluded subreddits list to protect important content
- Keyword-based exclusion
- Configurable delay between operations to respect API limits
- Comprehensive error handling and logging
- Backup of deleted content

## System Requirements

- [![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/) Python 3.6 or higher
- [![PRAW](https://img.shields.io/badge/PRAW-7.0+-green.svg)](https://praw.readthedocs.io/en/stable/) PRAW (Python Reddit API Wrapper)
- [![tqdm](https://img.shields.io/badge/tqdm-4.0+-orange.svg)](https://tqdm.github.io/) tqdm library to support real-time progress visualization during content removal operations
-  pytz library for timezone handling

## Installation

1. Clone the repository:
```bash
git clone https://github.com/905timur/Reddit-Content-Cleaner.git
cd Reddit-Content-Cleaner
```

2. Install required packages:
```bash
pip install praw pytz tqdm
```

## Configuration

## **REDDIT CONFIGURATION**

1. Navigate to [Reddit Apps Preferences](https://www.reddit.com/prefs/apps).

2. Click "Create application" at the bottom of the repository.

3. Select "script".

4. Fill out the description, and both the URL and redirect URI fields (you can point both fields to this GitHub page).

5. Click "create app".

    ![image](https://user-images.githubusercontent.com/130249301/234336730-dbe61b3f-ffed-4f1f-ab35-b5fe1239d72c.png)

6. Once your app is created, you will see your client ID and client secret. Both are highlighted below:

    ![image](https://user-images.githubusercontent.com/130249301/234361938-e09c0f87-e6b8-4b6b-9916-593b4bbcf35d.png)
### Credentials Setup

Create a file named `credentials.txt` in the script directory with the following format:
```
your_client_id
your_client_secret
your_reddit_username
your_reddit_password
```

### Configuration File

The script uses a `config.json` file for customization. It will be automatically created on first run with default values, or you can create it manually:

```json
{
    "replacement_text": ".",
    "min_delay": 6, 
    "max_delay": 8, 
    "excluded_subreddits": ["AskScience", "PersonalFinance", "LegalAdvice", "programming"],
    "excluded_keywords": ["important", "keep this", "legal document", "confidential"],
    "backup_enabled": true,
    "dry_run": false
}
```

Configuration options:
- `replacement_text`: Text to replace comments with before deletion
- `min_delay`: Minimum delay between operations in seconds
- `max_delay`: Maximum delay between operations in seconds
- `excluded_subreddits`: List of subreddits to exclude from deletion
- `excluded_keywords`: List of keywords that will prevent content deletion
- `backup_enabled`: Enable/disable content backups
- `dry_run`: Test mode that shows what would be deleted without actually deleting

## Usage

Run the script using:
```bash
python RedditContentCleaner.py
```

### Available Options

1. **Remove content older than x days**
   - Deletes all posts and comments older than the specified number of days
   - Prompts for the number of days
   - Respects excluded subreddits and keywords

2. **Remove comments with negative karma**
   - Automatically finds and removes all comments with negative karma scores
   - Useful for cleaning up controversial or downvoted comments

3. **Remove comments with 1 karma and no replies**
   - Cleans up comments that haven't received any engagement
   - Helps remove "orphaned" comments from your history

4. **Remove all posts**
   - Deletes all posts from your Reddit history

5. **Remove posts older than x days**
   - Deletes posts older than the specified number of days

6. **Remove posts under x upvotes**
   - Deletes posts with a score below the specified threshold

7. **Remove content from specific subreddit**
   - Target a specific subreddit for content cleanup
   - Useful for removing history from particular communities

8. **Remove content containing keyword**
   - Search and remove posts or comments containing specific words or phrases
   - Case-insensitive matching

9. **Edit configuration**
   - View current configuration settings
   - Provides instructions for modifying the config.json file

10. **Enable/Disable dry run**
   - Toggle test mode on/off
   - Shows what would be deleted without actually deleting
   - Useful for verifying settings before running cleanup

11. **Quit**
   - Safely exit the program

## Backup System

When enabled, the backup system creates a `deleted_content.txt` file containing:
- Timestamp of deletion
- Content score
- Subreddit name
- Original content (post or comment)
- Separator line for easy reading

Example backup entry:
```
Timestamp: 2025-01-06 12:34:56+00:00
Score: 1
Subreddit: AskReddit
Content: Original content text here
--------------------------------------------------
```

## Logging

The script maintains a `content_cleaner.log` file with detailed operation logs including:
- Timestamp of operations
- Success/failure status
- Error messages if any
- Affected subreddits

## Safety Features

### Rate Limiting
- Random delay between 6-8 seconds between operations
- Configurable through min_delay and max_delay settings
- Helps prevent Reddit API rate limit issues

### Content Protection
- Excluded subreddits list prevents accidental deletion of important content
- Keyword-based exclusion for protecting specific content
- Dry run mode for testing configuration changes
- Backup system for recovery if needed

## Error Handling

The script includes comprehensive error handling for:
- API connection issues
- Authentication problems
- Rate limiting errors
- File system errors
- Invalid input validation

## Best Practices

1. Always run in dry run mode first when making configuration changes
2. Keep backups enabled unless storage is a concern
3. Start with longer delays if unsure about rate limiting
4. Regularly update excluded subreddits list
5. Check logs periodically for any issues

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify credentials.txt format
   - Check Reddit API credentials
   - Ensure account password is correct

2. **Rate Limiting**
   - Increase min_delay and max_delay values
   - Check for other scripts using same account
   - Verify API usage limits

3. **Missing Content**
   - Check excluded_subreddits list
   - Verify excluded_keywords
   - Review log file for errors

### Getting Help

If you encounter issues:
1. Check the log file for error messages
2. Review configuration settings
3. Verify Reddit API status
4. Open an issue on this GitHub repository

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request
4. Include tests for new features
5. Update documentation as needed

## License

This project is licensed under the MIT License.

[![ License.](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Changelog

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
