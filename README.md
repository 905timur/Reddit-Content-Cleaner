# Reddit Content Cleaner Version 1.0.0
A Python script that helps you manage your Reddit content history by providing various options to clean, edit, and delete posts and comments based on different criteria. The script includes features like age-based deletion, karma-based filtering, and keyword-based management.

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

- Python 3.6 or higher
- PRAW (Python Reddit API Wrapper)
- pytz library for timezone handling

## Installation

1. Clone the repository:
```bash
git clone https://github.com/905timur/Reddit-Content-Cleaner-v2.git
cd Reddit-Content-Cleaner-v2
```

2. Install required packages:
```bash
pip install praw pytz
```

## Configuration

### Reddit API Setup

1. Go to Reddit's App Preferences page: https://www.reddit.com/prefs/apps/
2. Click "Create application" at the bottom
3. Select "script"
4. Fill in the required information:
   - Name: Your app name
   - Description: Brief description
   - About URL: This GitHub repository URL
   - Redirect URI: This GitHub repository URL
5. Click "create app"
6. Note down your client ID and client secret

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

## Changelog

### v2.0.0 (alpha)
- Added configuration file support
- Implemented dry run mode
- Added subreddit-specific deletion
- Added keyword-based deletion
- Improved logging and backup system
- Added type hints and better error handling
- Converted to class-based structure

### v1.9.1
- Added randomized 6-8 second delay between deletions
- API rate limit improvements

### v1.9
- Moved credentials to external file
- Updated datetime handling for timezone support
