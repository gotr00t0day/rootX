# rootX
rootX is a modern, feature-rich IRC client built with Python and Tkinter, offering a clean and intuitive graphical interface while maintaining powerful IRC functionality.

## Features

### Multi-Server Support
- Connect to multiple IRC servers simultaneously
- Server-specific channel management
- Individual server connection settings
- Easy server switching

### Channel Management
- Join multiple channels across different servers
- User list with operator/voice status indicators
- Channel operator controls (kick, ban, op/deop, voice/devoice)
- Channel modes and topic management
- Batch processing for efficient user list updates

### Private Messaging
- Dedicated windows for private conversations
- CTCP action support (/me commands)
- User-to-user messaging across servers

### Advanced IRC Features
- Full IRC command support
- WHOIS functionality
- Channel listing with search capability
- NickServ and ChanServ services support
- Away status management
- Nickname registration and authentication

### User Interface
- Modern tabbed interface
- Network tree for easy navigation
- Customizable themes
- Status window for server messages
- Intuitive context menus
- User-friendly dialog windows

### Theme System
- Multiple built-in themes (Default, Dark, Light, Matrix)
- Customizable colors for different message types
- Real-time theme switching
- Persistent theme settings

### Additional Features
- Automatic reconnection
- Error handling and recovery
- UTF-8 encoding support
- Logging capabilities
- Action message support
- User mode tracking

## Installation

### Clone the repository:

git clone https://github.com/gotr00t0day/rootX.git

### Install dependencies

pip3 install -r requirements.txt

## Usage

python3 rootX.py


### Basic Commands
- `/server <server> [port] [nickname]` - Connect to a server
- `/join #channel` - Join a channel
- `/msg <user> <message>` - Send private message
- `/me <action>` - Send action message
- `/quit [message]` - Disconnect from server

## Dependencies
- Python 3.x
- Tkinter
- Colorama

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Thanks to the Python IRC community
- Inspired by classic IRC clients while embracing modern design principles

---
Built with ❤️ by c0d3ninja



