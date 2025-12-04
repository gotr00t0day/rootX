# 🚀 RootX IRC Client v2

A powerful, scriptable IRC client with modern features and mIRC-style scripting.

## ✨ Features

- **Multi-Server Support** - Connect to multiple IRC servers simultaneously
- **mIRC-Style Scripting** - Full-featured scripting engine for automation
- **User Levels System** - Built-in permission/access control
- **Private Messages** - Tabbed PM interface
- **Channel Management** - Easy channel operations
- **Cross-Platform** - Works on macOS, Linux, Windows

## 📚 Documentation

- **[Scripting Tutorial](SCRIPTING_TUTORIAL.md)** - Complete beginner's guide to scripting
- **[Quick Reference](SCRIPTING_QUICKREF.md)** - One-page scripting cheat sheet
- **[User Levels Guide](USER_LEVELS_GUIDE.md)** - Access control system documentation

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running

```bash
python3 rootX.py
```

### Connecting to IRC

```
/server irc.libera.chat 6667 YourNickname
/join #channel
```

## 📝 Scripting

### Your First Script

Create `scripts/hello.rsx`:

```mirc
on TEXT:!hello:#:{
    msg $chan Hello, $nick!
}
```

Load it:
```
/script reload
```

### Learn More

- Check out `scripts/sample.rsx` for examples
- Read the [Scripting Tutorial](SCRIPTING_TUTORIAL.md) for complete guide
- See [Quick Reference](SCRIPTING_QUICKREF.md) for syntax

## 🎯 Example Scripts

### Auto-Welcome
```mirc
on JOIN:*:#:{
    msg $chan Welcome to $chan, $nick!
}
```

### Fun Commands
```mirc
on TEXT:!dice:#:{
    msg $chan $nick rolled: $rand(6)
}
```

### User Management
```mirc
on TEXT:!level*:#:{
    if ($level >= 500) {
        msg $chan You're an admin!
    }
}
```

## 🔧 Script Commands

| Command | Description |
|---------|-------------|
| `/script reload` | Reload all scripts |
| `/script unload` | Unload all scripts |
| `/script list` | Show loaded scripts |
| `/script load <file>` | Load specific script |

## 🎨 Customization

Scripts are stored in `/scripts/` folder:
- `sample.rsx` - Basic examples
- `userlevels.rsx` - Advanced user management
- `autoconnect.rsx` - Server automation

## 💡 Tips

1. Use `/script reload` after editing scripts
2. Check console output for errors
3. Use `echo` in scripts for debugging
4. Start with simple scripts and build up

## 📖 Full Documentation

- **[Essential Features](ESSENTIAL_FEATURES.md)**: Complete guide to all mIRC features ✨
- **[Scripting Tutorial](tutorials/SCRIPTING_TUTORIAL.md)**: Complete guide with exercises
- **[Quick Reference](tutorials/SCRIPTING_QUICKREF.md)**: One-page cheat sheet
- **Examples**: `scripts/features_demo.rsx` - Interactive demo of all features

---

**Made with ❤️ for the IRC community**

