# Evolving Beasts

[![project badge](https://img.shields.io/badge/1chooo-monster__bot-informational)](https://github.com/1chooo/monster-bot)
[![Made with Python](https://img.shields.io/badge/Python=3.9-blue?logo=python&logoColor=white)](https://python.org "Go to Python homepage")
[![License](https://img.shields.io/badge/License-MIT-blue)](./LICENSE "Go to license section")

A brief summary of the project
---

**[Evolving Beasts](https://lin.ee/gEbeKQV)**, the **LINE BOT** supernova that seamlessly blends ***gaming, quests, nurturing, AI, and sustainability concepts***.

| [Weather Shakespeare](https://weather-shakespeare.github.io/) | LINE QRCODE |
|:-:|:-:|
| <img src="imgs/profile.jpg" width="300">| <img src="imgs/L_gainfriends_2dbarcodes_BW.png" width="300"> |

Enviroment: 
---

### With pip vertial environment
python request: `3.9.6`

#### For **Linux/MacOS**
```shell
$ pip3 install virtualenv
$ virtualenv venv --python=python3.9.6
$ source venv/bin/activate
$ pip install -r requirements.txt
$ deactivate
$ rm -rf venv     # remove the venv
```

#### For **Windows**
```shell
$ pip install virtualenv
$ virtualenv venv
$ venv\Scripts\activate
$ pip install -r requirements.txt
$ deactivate
$ rmdir /s venv     # remove the venv
```

### Add LINE BOT Developer Config

You should duplicate the file `config/linebot_template.conf` and rename into `config/linebot.conf`

```js
{
    "CHANNEL_ACCESS_TOKEN": "YOUR_CHANNEL_ACCESS_TOKEN",    // LINE BOT API
    "CHANNEL_SECRET": "YOUR_CHANNEL_SECRET"                 // LINE BOT Handler
}
```


### With ngrok free server
```SHELL
$ brew install ngrok --cask
$ ngrok config add-authtoken YOUR_TOKEN
$ python run.py
$ ngrok http 5002
```

### Start multiple tunnel

```shell
$ ngrok config check
Valid configuration file at YOUR_PATH/ngrok/ngrok.yml
```

Add the below code in `YOUR_PATH/ngrok/ngrok.yml`

```yml
version: "2"
authtoken: "YOUR_TOKEN"
# Please avoid making any changes to the content provided below
tunnels:
  first:
    addr: 5002
    proto: http    
  second:
    addr: 5012
    proto: http
```

type `ngrok start --all` in terminal to start `ngrok`

```shell
$ mkdocs build
$ mkdocs serve
```
Workflow permissions
- [x] Read and Write Permissions

Project Structure
---
```
PROJECT_ROOT
├── test/
│   ├── test_main.py/
│   ├──   :
│   └──   :
├── Monster/
│   ├── Drama.py
│   ├── Utils.py
│   └──   :
├── config/
│   ├── linebot.conf
│   ├── chatgpt.conf
│   └──   :
├── log/
│   ├── date/
│   └──   :
├── run.py
├── LICENSE
└── README.md
```

License
---
Released under [MIT](./LICENSE) by [@1chooo](https://github.com/1chooo), [@Weather-Shakespeare](https://github.com/Weather-Shakespeare).

This software can be modified and reused without restriction.
The original license must be included with any copies of this software.
If a significant portion of the source code is used, please provide a link back to this repository.