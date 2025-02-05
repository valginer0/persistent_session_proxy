#!/bin/bash
# Setup script for Persistent Session Proxy on Ubuntu/Debian

# Update system
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-venv nginx supervisor

# Create a user for the proxy
sudo useradd -m -s /bin/bash proxy_user

# Create directory for the application
sudo mkdir -p /opt/persistent-proxy
sudo chown proxy_user:proxy_user /opt/persistent-proxy

# Clone the repository (replace with your repo URL)
sudo -u proxy_user git clone https://github.com/yourusername/persistent_session_proxy.git /opt/persistent-proxy

# Install dependencies directly
sudo -u proxy_user python3 -m pip install --user -r /opt/persistent-proxy/requirements.txt

# Create supervisor config
cat << EOF | sudo tee /etc/supervisor/conf.d/persistent-proxy.conf
[program:persistent-proxy]
directory=/opt/persistent-proxy
command=python3 /opt/persistent-proxy/run_proxy.py --host 127.0.0.1 --port 8080
user=proxy_user
autostart=true
autorestart=true
stderr_logfile=/var/log/persistent-proxy.err.log
stdout_logfile=/var/log/persistent-proxy.out.log
EOF

# Create nginx config for SSL termination
cat << EOF | sudo tee /etc/nginx/sites-available/persistent-proxy
server {
    listen 443 ssl;
    server_name proxy.yourdomain.com;  # Replace with your domain

    ssl_certificate /etc/letsencrypt/live/proxy.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/proxy.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/persistent-proxy /etc/nginx/sites-enabled/

# Reload services
sudo supervisorctl reread
sudo supervisorctl update
sudo systemctl restart nginx
