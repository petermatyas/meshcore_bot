# meshcore_bot





# create service
sudo nano /etc/systemd/system/mcbot.service

```
[Unit]
Description=Meshcore bot
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/my-script.py
Restart=always
User=myuser
Group=mygroup

[Install]
WantedBy=multi-user.target

```



