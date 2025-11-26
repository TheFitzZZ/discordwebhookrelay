# Discord Webhook Relay

Small container that ingests webhooks from Kopia, reformats them into a Discord compatible format, and sends them to Discord.

## Features

- **Webhook Endpoint**: Ingests notifications (Text or HTML).
- **Admin UI**: Simple web interface to manage endpoints.
- **Configuration**: Persisted via YAML file.
- **Dockerized**: Lightweight container.

## Usage

### 1. Build the Image

```bash
./build-and-push.sh
```

(Make sure to update the `REGISTRY` variable in `build-and-push.sh` first)

### 2. Run the Container

```bash
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/config:/app/config \
  your-registry/discord-webhook-relay
```

### 3. Configure

1.  Open `http://localhost:5000/admin` in your browser.
2.  Add a new endpoint:
    *   **Name**: A friendly name (e.g., "Kopia Backup").
    *   **Type**: `txt` or `html` (depending on what Kopia sends).
    *   **Discord Webhook URL**: The webhook URL from your Discord channel integration.
3.  Copy the generated **Webhook URL (Ingest)** (e.g., `/webhook/uuid...`).

### 4. Configure Kopia

Use the generated ingest URL in Kopia's webhook settings.
Example: `http://your-container-ip:5000/webhook/<uuid>`

## Configuration File

The configuration is saved in `config/config.yaml` inside the container (mapped to your local `config` directory).

```yaml
endpoints:
  - id: "uuid..."
    name: "My Backup"
    type: "txt"
    discord_url: "https://discord.com/api/webhooks/..."
```
