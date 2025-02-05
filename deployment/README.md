# Deploying Persistent Session Proxy

## Option 1: DigitalOcean Droplet (Recommended)

1. Create a DigitalOcean account
2. Create a new Droplet:
   - Choose Ubuntu 22.04 LTS
   - Basic plan ($5/month)
   - Any region close to you
   - Add your SSH key

3. Point a domain to your server (optional but recommended):
   - Add an A record in your DNS settings
   - Point it to your droplet's IP address

4. SSH into your server:
```bash
ssh root@your-server-ip
```

5. Run the setup script:
```bash
# Download the setup script
wget https://raw.githubusercontent.com/yourusername/persistent_session_proxy/main/deployment/setup_vps.sh

# Make it executable
chmod +x setup_vps.sh

# Run it
./setup_vps.sh
```

6. Configure your browser:
   - Open browser settings
   - Find proxy settings
   - Set HTTP proxy to:
     * Host: your-server-ip (or your domain)
     * Port: 443 (if using SSL) or 8080 (if not)

## Option 2: Oracle Cloud Free Tier

Oracle Cloud offers a free tier that includes 2 small VMs. Follow the same steps as above, but:
1. Create Oracle Cloud account
2. Launch an "Always Free" VM
3. Use Ubuntu 22.04
4. Follow the same setup steps as DigitalOcean

## Option 3: Local Network Computer

If you have a spare computer that can stay on:

1. Install Ubuntu or Windows
2. Install Python 3.8 or higher
3. Clone the repository
4. Install dependencies:
```bash
pip install -r requirements.txt
```
5. Run the proxy:
```bash
python run_proxy.py --host 0.0.0.0 --port 8080
```

## Security Considerations

1. Always use HTTPS in production:
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d proxy.yourdomain.com
```

2. Set up a firewall:
```bash
sudo ufw allow ssh
sudo ufw allow 443/tcp  # If using SSL
sudo ufw allow 8080/tcp # If not using SSL
sudo ufw enable
```

3. Keep system updated:
```bash
sudo apt update
sudo apt upgrade -y
```
