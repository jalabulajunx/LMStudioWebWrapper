# LM Studio Web Chat Interface

A web-based chat application that provides a multi-user interface for interacting with LM Studio's local LLMs. This application supports both general conversations and specialized music database queries, with real-time streaming responses and session management.

## Note
- The entire source code was written with Claude.ai
- I used an extensive prompting to get the desired output
- This is work-in-progress

<details>
  <summary>The Prompt</summary>
I have an idea of developing a web chat application sitting on top of LM Stuido SDK. I hope you are familiar with it. This application would be for my family to use the local LLMs instead of the publicly available ones. The LM Studio Server is housed within ArchLinux. This web application would be deployed on the same server. 

The web application should be with the following stack:
	1. Python
	2. JavaScript/jQuery
	3. HTML
	4. CSS
	
Architectural considerations:
	1. Modular - each piece of feature should be its own file
	2. Comments - every function, class and file should be well documented
	3. Maintenance - the code generated should be maintainable
	4. Follow good architectural and coding practices
	5. Should be performant
	6. You'll write unit tests and validate if your code works
	
Deployment considerations:
	1. ArhcLinux OS
	2. Home network
	3. Will run as a service - systemd
	4. You'll inform me what additional packages need to be installed to run this chat program
	5. You'll tell me how to test it without running as a service
	
The requirements:
	1. Users are to be authenticated and thus can logout of their sessions
	2. Users will have their own sessions
	3. Users will not see other users or other users' chats
	4. Users can see their past chat history from previous sessions
	5. Users can modify/rename or delete their past chat titles
	6. Modifying chat titles should not reorder past chat conversations
	7. Users can ask any questions - small or larger in text size
	8. Users can stop from the response being generated
	9. Users would see streaming response from server
	10. Users will option to use a "general task" and another task that would allow them to ask questions about a specific database
		a. That specific database is Music database fed by either a spreadsheet or sqlLite
		b. Their normal questions should be converted to Select statements by a query out to LM Studio
		c. The response statement should be validated if it is a properly formed SQL query
		d. That SQL query should be executed and the results are to be sent to LM Studio for it to be converted to a response that end user can understand instead of a bunch of columns and rows. For instance, if the user submits a query "Find me all the albums whose composer is A. R. Rahman", then the LM Studio should then produce a SQL statement as "Select album from <DATABASE TABLE> Where albumartist like %rahman%" - it should be case insensitive retrieval. The result is to be fed again to LM Studio to be formulated as a response like "A. R. Rahman was the composer of several albums such as <Albums from SQL Query>"
		
Design considerations:
	1. UI should be two-paneled layout
		a. Left pane: chat history; right pane: chat conversations
	2. Intuitive UI placements for:
		a. Rename/Delete for each conversation thread
		b. Create new conversation
		c. Send chat
		d. Stop chat
		e. Tasks: General and Music Queries
		f. Logout
		g. Responsive on different screens and resolution
		h. Good colour variations on the entire application
	3. Will be used by all ages
</details>

## Features

### Core Functionality
- Real-time chat interface with streaming responses
- Multi-user support with authentication
- Session persistence and chat history
- Two-task mode:
  - General conversations
  - Music database queries with natural language processing
- WebSocket-based real-time communication
- Response interruption capability

### User Interface
- Two-panel layout:
  - Left panel: Chat history and management
  - Right panel: Active conversation
- Responsive design for various screen sizes
- Intuitive controls for:
  - Creating new conversations
  - Renaming chat sessions
  - Deleting conversations
  - Switching between task modes
  - Stopping response generation

### Security
- User authentication and session management
- SQL injection prevention
- Rate limiting
- Secure headers
- XSS protection
- CSRF protection

## Technical Stack

### Backend
- Python 3.8+
- Flask web framework
- Flask-SocketIO for real-time communication
- SQLAlchemy for database management
- LM Studio SDK for LLM integration

### Frontend
- HTML5
- CSS3
- JavaScript (vanilla)
- WebSocket for real-time updates

### Database
- SQLite
- Support for custom music database integration

## Installation

### Prerequisites
- Python 3.8 or higher
- LM Studio Server running locally
- ArchLinux (for deployment instructions; adaptable to other systems)

### System Dependencies
```bash
# Install system packages
sudo pacman -S python python-pip sqlite
```

### Python Dependencies
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### Configuration
1. Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///app.db
LM_STUDIO_URL=http://localhost:1234/v1
FLASK_ENV=development  # or production
```

2. Initialize the database:
```bash
flask db upgrade
```

## Running the Application

### Development Mode
```bash
python run.py
```
The application will be available at `http://localhost:5000`

### Production Deployment
1. Create a systemd service file:
```bash
sudo nano /etc/systemd/system/webchat.service
```

2. Add the following content:
```ini
[Unit]
Description=Web Chat Application
After=network.target

[Service]
Type=simple
User=webchat
WorkingDirectory=/opt/webchat
Environment=FLASK_ENV=production
ExecStart=/opt/webchat/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Start and enable the service:
```bash
sudo systemctl start webchat
sudo systemctl enable webchat
```

## Usage

1. Access the web interface through your browser
2. Register a new account or log in
3. Create a new chat session
4. Select task mode:
   - General: For regular conversations
   - Music: For music database queries
5. Start chatting!

### Music Database Integration
To use the music database feature:
1. Prepare your music database in SQLite format
2. Update the database path in configuration
3. Use natural language queries to search your music collection

## Development

### Project Structure
```
chat_app/
├── config/
│   ├── __init__.py
│   └── settings.py
├── server/
│   ├── __init__.py
│   ├── app.py
│   ├── auth.py
│   ├── chat.py
│   ├── database.py
│   ├── llm.py
│   ├── music.py
│   └── websocket.py
├── static/
│   ├── css/
│   └── js/
├── templates/
├── tests/
└── run.py
```

### Running Tests
```bash
pytest tests/
```

## Security Considerations
- Always change the default secret key
- Use HTTPS in production
- Regularly update dependencies
- Monitor system logs
- Back up user data regularly
- Review LM Studio access controls

## Performance Optimization
- Database connection pooling
- Query result caching
- WebSocket message batching
- Frontend asset minification
- Response streaming for large messages

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License - See LICENSE file for details

## Acknowledgments
- LM Studio team for the local LLM capabilities
- Flask and its extension authors
- SQLAlchemy team

## Support
For issues and feature requests, please use the GitHub issue tracker.

## Roadmap
- Docker containerization
- User preference settings
- Advanced music query features
- Chat export functionality
- API documentation
- Multi-model support


