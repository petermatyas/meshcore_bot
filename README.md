# meshcore_bot





# create service
sudo nano /etc/systemd/system/meshcore_bot.service

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



sudo systemctl daemon-reload
sudo systemctl enable meshcore_bot.service
sudo systemctl start meshcore_bot.service

