# Asterisk ConfBridge Manager

**MAINTAINER IS WANTED** If you would like to maintain this repo pls create a new ticket.

This is a WEB based interface for managing Asterisk ConfBridge application.

**Built on Asterisk ConfBridge, Flask, SSE, React.js**

You can request a [new feature](https://github.com/dessanhemrayev/astconfman/issues/new) or see current requests and bugs [here](https://github.com/dessanhemrayev/astconfman/issues).

> **Repository**: https://github.com/dessanhemrayev/astconfman

---

## How it works

Flask is used as a WEB server. By default it uses SQLite3 database for storage but other datasources are also supported (see `config.py`). 

Conference participants are invited using Asterisk call out files. To track participant dial status local channel is used. No AMI/AGI/ARI is used. Everything is built around `asterisk -rx 'confbridge <...>'` CLI commands. Asterisk and Flask are supposed to be run on the same server but it's possible to implement remote asterisk command execution via SSH. The software is distributed as as on BSD license. Asterisk resellers can easily implement their own logo and footer and freely redistribute it to own customers (see `BRAND_` options in `config.py`).

---

## Features

* Private (only for configured participants) and public (guests can join) conferences.
* Muted participant can indicate unmute request. 
* Contact management (addressbook) with import contacts feature.
* Conference recording (always / ondemand, web access to recordings).
* Support for dynamic ConfBridge [profiles](https://wiki.asterisk.org/wiki/display/AST/ConfBridge#ConfBridge-BridgeProfileConfigurationOptions) (any profile option can be set).
* Invite participants from WEB or phone (on press DTMF digit).
* Invite guests on demand by phone number.
* Conference management:
  * Lock / unlock conference;
  * Kick one / all;
  * Mute / unmute one / all 
* Realtime conference events log (enter, leave, kicked, mute / unmute, dial status, etc)
* Asterisk integrators re-branding ready (change logo, banner, footer)

---

## Demo

![atsconf](https://user-images.githubusercontent.com/14130087/154665193-1a5e98c8-ea81-4689-b75e-b5e81528301c.png)

Here is the demo with the following scenario:
* Import contacts.
* Add contacts to participants.
* Invite all participants into conference.
* Enter conference from phone.
* Unmute request from phone.
* Invite customer by his PSTN number.
* Enter non-public conference.

[![Demo](http://img.youtube.com/vi/R1EV4D8cFj8/0.jpg)](https://youtu.be/R1EV4D8cFj8 "Demo")

---

## Installation

### Requirements

* **Asterisk 18+** (ConfBridge with support for flags: `muted`, `admin`, `marked`)
* **Python 3.12**
* Flask, React.js, SSE
* SQLite3 (or other database via `config.py`)

On Ubuntu/Debian:
```bash
sudo apt-get install python3.12 python3.12-venv python3.12-dev python3-pip
```

> ⚠️ **Important**: Ensure Asterisk has `CURL` function compiled and loaded. Check with:
> ```
> *CLI> core show function CURL
> *CLI> module show like confbridge
> ```

### Download and Setup

```bash
# Clone the repository
git clone https://github.com/dessanhemrayev/astconfman.git
cd astconfman

# Create virtual environment with Python 3.12
python3.12 -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database and run the server
flask --app run.py init
flask --app run.py run
```

Now visit `http://localhost:5000/` in your browser.

> 🔐 **Default credentials**: `admin / admin` — change immediately after first login!

---

## Configuration

### WEB server configuration

Go to `instance` folder and create `config.py` file with your local settings. See [config.py](https://github.com/dessanhemrayev/astconfman/blob/master/astconfman/config.py) for possible options to override. Options in `config.py` are self-descriptive.

### Asterisk configuration

1. Ensure in `/etc/asterisk/asterisk.conf`:
   ```ini
   live_dangerously = no
   ```

2. Include project files in your Asterisk config:
   ```ini
   # In /etc/asterisk/extensions.conf
   #include /path/to/astconfman/asterisk_etc/extensions.conf

   # In /etc/asterisk/confbridge.conf  
   #include /path/to/astconfman/asterisk_etc/confbridge.conf
   ```

3. Set your settings in `[globals]` section of `extensions.conf`:
   ```ini
   CONFMAN_HOST=http://localhost:5000
   CONFMAN_CONTEXT=confman-dialout
   ```

4. Reload Asterisk configuration:
   ```
   *CLI> core reload
   *CLI> confbridge reload
   ```

---

## Participant menu (DTMF)

While in the conference participants can use the following DTMF options:

| Key | Action |
|-----|--------|
| 1 | Toggle mute / unmute myself |
| 2 | Unmute request |
| 3 | Toggle mute all participants (admin profile only) |
| 4 | Decrease listening volume |
| 5 | Reset listening volume |
| 6 | Increase listening volume |
| 7 | Decrease talking volume |
| 8 | Reset talking volume |
| 9 | Increase talking volume |
| 0 | Invite all / not yet connected participants (admin profile only) |

---

## Dialplan for calling external users

```ini
[confman-dialout]
include => localph
include => extph

[localph]
exten => _XXX,1,Dial(SIP/${EXTEN},60)
exten => _XXX,2,Set(ret=${CURL(${CONFMAN_HOST}/asterisk/dial_status/${conf_number}/${participant_number}/${DIALSTATUS})})

[extph]
exten => _XXXX.,1,Dial(${DIALOUT_TRUNK1}/${EXTEN},60)
exten => _XXXX.,2,Set(ret=${CURL(${CONFMAN_HOST}/asterisk/dial_status/${conf_number}/${participant_number}/${DIALSTATUS})})
```

---

## Troubleshooting

### Asterisk monitor path not accessible

```
IOError: FileAdmin path "/var/spool/asterisk/monitor/" does not exist or is not accessible
```

**Solution**: Add the user running astconfman to the `asterisk` group:
```bash
sudo usermod -a -G asterisk <username>
```

### Conference makes multiple outgoing calls on dialout call

**Check**:
1. Is `run.py` running with the same user as Asterisk?
2. Does the `env` directory have read-write access for the Asterisk user?


---

## Links

* **Repository**: https://github.com/dessanhemrayev/astconfman
* **ConfBridge Documentation**: https://wiki.asterisk.org/wiki/display/AST/ConfBridge
* **Flask Docs**: https://flask.palletsprojects.com/

---

> ℹ️ **MAINTAINER IS WANTED**  
> If you would like to maintain this repo please create a new ticket in [Issues](https://github.com/dessanhemrayev/astconfman/issues).
