# Run

### Create virtual env
```bash
conda create --name NAME python=3.10
conda activate NAME
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Compile translations

```bash
pybabel compile -d translations
```

### Run

```bash
flask run
```

### Open locally

Go to `http://127.0.0.1:5000/`





# Deployment and Security

- <b>Hosting</b>: Get a Virtual Private Server (VPS) from a provider like DigitalOcean, Vultron, or Linode.
- <b>Web Server (Nginx)</b>: Install and configure Nginx to act as a reverse proxy. It will receive public traffic and forward it to your Flask application (which you'll run with Gunicorn, a production-ready server).
- <b>SSL (Let's Encrypt)</b>: Use a tool like certbot to get a free SSL certificate for your domain, enabling HTTPS.
- <b>DDoS Protection (Cloudflare)</b>: This is the easiest way to get robust DDoS protection and SSL. Sign up for a free Cloudflare account and point your domain's nameservers to them. Cloudflare will then manage traffic to your server.