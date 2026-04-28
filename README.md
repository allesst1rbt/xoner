# XoneCloud API Scripts

Reverse-engineered API client for [portal.xonecloud.com.br](https://portal.xonecloud.com.br).

## Architecture

| Service | Base URL | Purpose |
|---------|----------|---------|
| user-api | `user-api.xonecloud.com` | Auth, users, company settings, access tokens |
| register-api | `register-api.xonecloud.com` | Collaborators, agents, departments, software, WiFi |
| dashboard-api | `dashboard-api.xonecloud.com` | Productivity metrics, behavior, geolocation |
| report-api | `report-api.xonecloud.com` | Report generation & download |
| billing-api | `billing-api.xonecloud.com` | Plans, agent usage |
| coreregistry-api | `coreregistry-api.xonecloud.com/api` | Alerts, rules, webhooks |
| notification-api | `wrapper-notification-api.xonecloud.com` | Notifications |
| gateway-api | `gateway-api.xonecloud.com` | Support tickets |
| agentcomm-api | `agentcomm-api.xonecloud.com` | Agent heartbeat/events (token-based) |

## Authentication

Local login (username + password):
```bash
POST user-api.xonecloud.com/auth/signin?lang=pt-BR
{"username": "user@company.com", "password": "password"}
```

Returns `{success, message, payload: [{token, ...}]}`. Use `Authorization: Bearer <token>` on all subsequent calls.

Azure AD login is also supported via `auth/signin/azure-ad`.

## Usage

```python
from client import XoneClient

client = XoneClient("user@company.com", "password")
client.login()

# Users
me = client.get_me()
users = client.get_users()

# Collaborators
collabs = client.get_collaborators()

# Dashboard
from datetime import date, timedelta
end = date.today().isoformat()
start = (date.today() - timedelta(days=7)).isoformat()

activity = client.get_productivity(start, end)
journey = client.get_journey_adherence(start, end)
inactivity = client.get_inactivity(start, end)

# Agents
agents = client.get_agent_users()

# Notifications
notifs = client.get_notifications()
```

## CLI

```bash
python client.py user@company.com password get_me
python client.py user@company.com password get_collaborators
python client.py user@company.com password get_departments
python client.py user@company.com password list_reports
```

## Agent Token Auth (agentcomm-api)

The agent uses a separate token-based auth (not JWT). The `AgentToken` is provisioned
during agent installation via `TOKEN=<token> dpkg -i xone-setup.deb`.
The agent then calls `agentcomm-api.xonecloud.com` with this token via Authorization header.

## Notes

- The DLLs in the `.deb` package are obfuscated with SmartAssembly 8.2.1
- The frontend app is Angular with Azure AD (MSAL) integration
- Agent components: HeartBeat, EventSender, LicenseManager, ProcessRunner, UpdateManager, UserActivity, Hardware
