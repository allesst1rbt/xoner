"""
XoneCloud API Client
Reverse-engineered from app.xonecloud.com JS bundle + .deb package analysis.

Auth: POST user-api.xonecloud.com/auth/signin {username, password} -> JWT
All authenticated requests: Authorization: Bearer <token>

Usage:
    client = XoneClient("your@email.com", "yourpassword")
    client.login()
    users = client.get_users()
"""

import requests
from typing import Optional, Any

BASE_URLS = {
    "user":        "https://user-api.xonecloud.com/",
    "register":    "https://register-api.xonecloud.com/",
    "dashboard":   "https://dashboard-api.xonecloud.com/",
    "report":      "https://report-api.xonecloud.com/",
    "billing":     "https://billing-api.xonecloud.com/",
    "gateway":     "https://gateway-api.xonecloud.com/",
    "integration": "https://integration-api.xonecloud.com/",
    "registry":    "https://coreregistry-api.xonecloud.com/api/",
    "notification":"https://wrapper-notification-api.xonecloud.com/",
    "agentcomm":   "https://agentcomm-api.xonecloud.com/",
}


class XoneClient:
    def __init__(self, username: str, password: str, lang: str = "pt-BR"):
        self.username = username
        self.password = password
        self.lang = lang
        self.token: Optional[str] = None
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    # ── Auth ──────────────────────────────────────────────────────────────────

    def login(self) -> dict:
        """Authenticate and store the JWT token."""
        resp = self.session.post(
            f"{BASE_URLS['user']}auth/signin?lang={self.lang}",
            json={"username": self.username, "password": self.password},
        )
        data = resp.json()
        if not data.get("success"):
            raise ValueError(f"Login failed: {data.get('message')}")
        # Token is either in payload[0].token or payload[0].accessToken
        payload = data.get("payload", [{}])
        token_entry = payload[0] if payload else {}
        self.token = (
            token_entry.get("token")
            or token_entry.get("accessToken")
            or token_entry.get("access_token")
        )
        if self.token:
            self.session.headers["Authorization"] = f"Bearer {self.token}"
        return data

    def logout(self) -> dict:
        return self._get("user", f"auth/signout?lang={self.lang}")

    def refresh_token(self) -> dict:
        return self._get("user", "auth/refresh")

    # ── Users ─────────────────────────────────────────────────────────────────

    def get_me(self) -> dict:
        return self._get("user", "me")

    def get_users(self, **params) -> dict:
        return self._get("user", f"user?lang={self.lang}", params=params)

    def get_user(self, user_id: str) -> dict:
        return self._get("user", f"user/{user_id}?lang={self.lang}")

    def get_self(self) -> dict:
        return self._get("user", f"user/self?lang={self.lang}")

    def update_user(self, user_id: str, data: dict) -> dict:
        return self._put("user", f"user/{user_id}?lang={self.lang}", data)

    def change_password(self, user_id: str, data: dict) -> dict:
        return self._put("user", f"user/{user_id}/password", data)

    def upload_user_photo(self, user_id: str, file_bytes: bytes) -> dict:
        return self._post("user", f"user/photo/{user_id}", data=file_bytes)

    # ── Access Tokens (API keys) ───────────────────────────────────────────────

    def get_access_tokens(self) -> dict:
        return self._get("user", "access-token")

    def get_access_token(self, token_id: str) -> dict:
        return self._get("user", f"access-token/{token_id}")

    def regenerate_access_token(self, token_id: str) -> dict:
        return self._post("user", f"access-token/regenerate/{token_id}", {})

    def get_company_jwt(self, company_id: str) -> dict:
        return self._get("user", f"company/{company_id}/token/jwt")

    # ── Company settings ──────────────────────────────────────────────────────

    def get_company_parameters(self) -> dict:
        return self._get("user", "company-parameters")

    def reset_company_parameters(self) -> dict:
        return self._post("user", "company-parameters/reset-default", {})

    def get_company_categories(self) -> dict:
        return self._get("user", "company-categories/list")

    def toggle_company_category(self, category_id: str) -> dict:
        return self._post("user", f"company-categories/toggleCompanyCategory/{category_id}?lang={self.lang}", {})

    # ── Collaborators (register-api) ──────────────────────────────────────────

    def get_collaborators(self, **params) -> dict:
        return self._get("register", f"collaborators?lang={self.lang}", params=params)

    def get_all_collaborators(self) -> dict:
        return self._get("register", "collaborators/all")

    def get_collaborator(self, collab_id: str) -> dict:
        return self._get("register", f"collaborators/{collab_id}?lang={self.lang}")

    def update_collaborator(self, collab_id: str, data: dict) -> dict:
        return self._put("register", f"collaborators/{collab_id}?lang={self.lang}", data)

    def delete_collaborator(self, collab_id: str) -> dict:
        return self._delete("register", f"collaborators/{collab_id}?lang={self.lang}")

    def get_all_users_access(self) -> dict:
        return self._get("register", "collaborators/getAllUsers")

    # ── Departments ───────────────────────────────────────────────────────────

    def get_departments(self) -> dict:
        return self._get("register", "departments")

    # ── Agents (register-api) ─────────────────────────────────────────────────

    def get_agents_count(self) -> dict:
        return self._get("register", "count")

    def get_agent_users(self, **params) -> dict:
        from urllib.parse import urlencode
        qs = urlencode(params)
        return self._get("register", f"agentusers/getAllComplete?{qs}")

    def get_agents_licensing(self, **params) -> dict:
        from urllib.parse import urlencode
        qs = urlencode(params)
        return self._get("register", f"agentusers/getLicenseByAgents?{qs}")

    def update_agent_user(self, agent_id: str, data: dict) -> dict:
        return self._put("register", f"agentusers/{agent_id}", data)

    def get_agent_installer_link(self, os: str, architecture: str) -> dict:
        return self._get("register", f"agent-installer?os={os}&architecture={architecture}")

    # ── Software & Sites ──────────────────────────────────────────────────────

    def get_softwares(self) -> dict:
        return self._get("register", "softwares/all/corporate")

    def get_software_category(self, software: str) -> dict:
        from urllib.parse import quote
        return self._get("register", f"softwares/{quote(software)}/category?lang={self.lang}")

    def get_site_categories(self) -> dict:
        return self._get("register", f"softwares/categories/global?lang={self.lang}")

    def get_sites_by_domain(self, domain: str) -> dict:
        return self._get("register", f"sites/byDomain/{domain}?lang={self.lang}")

    # ── Working days & Holidays ───────────────────────────────────────────────

    def get_working_days(self) -> dict:
        return self._get("register", f"workingday?lang={self.lang}")

    def get_holidays(self) -> dict:
        return self._get("register", "holiday")

    def create_holiday(self, data: dict) -> dict:
        return self._post("register", "holiday", data)

    def update_holiday(self, holiday_id: str, data: dict) -> dict:
        return self._put("register", f"holiday/{holiday_id}", data)

    def delete_holiday(self, holiday_id: str) -> dict:
        return self._delete("register", f"holiday/{holiday_id}")

    # ── Wi-Fi corporate ───────────────────────────────────────────────────────

    def get_wifi_networks(self) -> dict:
        return self._get("register", f"wifi-corporate?lang={self.lang}")

    def create_wifi_network(self, data: dict) -> dict:
        return self._post("register", f"wifi-corporate?lang={self.lang}", data)

    def update_wifi_network(self, wifi_id: str, data: dict) -> dict:
        return self._put("register", f"wifi-corporate/{wifi_id}?lang={self.lang}", data)

    def delete_wifi_network(self, wifi_id: str) -> dict:
        return self._delete("register", f"wifi-corporate/{wifi_id}?lang={self.lang}")

    # ── Dashboard ─────────────────────────────────────────────────────────────

    def get_productivity(self, begin_date: str, end_date: str, timezone: str = "America/Sao_Paulo") -> dict:
        return self._get("dashboard", f"dashboard/productivity/digital-activity?type=last_day&beginDate={begin_date}&endDate={end_date}&timezone={timezone}")

    def get_journey_adherence(self, begin_date: str, end_date: str, timezone: str = "America/Sao_Paulo") -> dict:
        return self._get("dashboard", f"dashboard/productivity/journey-adherence?type=last_day&beginDate={begin_date}&endDate={end_date}&timezone={timezone}")

    def get_inactivity(self, begin_date: str, end_date: str, timezone: str = "America/Sao_Paulo") -> dict:
        return self._get("dashboard", f"dashboard/productivity/inactivity?type=last_day&beginDate={begin_date}&endDate={end_date}&timezone={timezone}")

    def get_internet_activity(self, begin_date: str, end_date: str, timezone: str = "America/Sao_Paulo") -> dict:
        return self._get("dashboard", f"dashboard/productivity/internet-activity?type=last_day&beginDate={begin_date}&endDate={end_date}&timezone={timezone}")

    def get_systemic_wait(self, begin_date: str, end_date: str, timezone: str = "America/Sao_Paulo") -> dict:
        return self._get("dashboard", f"dashboard/productivity/systemic-wait?type=last_day&beginDate={begin_date}&endDate={end_date}&timezone={timezone}")

    def get_user_activity(self, username: str, begin_date: str, end_date: str, timezone: str = "America/Sao_Paulo") -> dict:
        return self._get("dashboard", f"analysis/user?beginDate={begin_date}&endDate={end_date}&username={username}&timezone={timezone}")

    def get_user_software_usage(self, username: str, begin_date: str, end_date: str, timezone: str = "America/Sao_Paulo") -> dict:
        return self._get("dashboard", f"analysis/user/software-timeline?beginDate={begin_date}&endDate={end_date}&username={username}&timezone={timezone}")

    def get_behavior(self, begin_date: str, end_date: str, timezone: str = "America/Sao_Paulo") -> dict:
        return self._get("dashboard", f"dashboard/productivity/behavior?beginDate={begin_date}&endDate={end_date}&timezone={timezone}")

    def get_geolocation(self, begin_date: str, end_date: str, timezone: str = "America/Sao_Paulo") -> dict:
        return self._get("dashboard", f"dashboard/productivity/behavior-geolocation?beginDate={begin_date}&endDate={end_date}&timezone={timezone}")

    def get_workstation_monitoring(self, begin_date: str, end_date: str, timezone: str = "America/Sao_Paulo") -> dict:
        return self._get("dashboard", f"dashboard/monitoring-hardware-hosts?beginDate={begin_date}&endDate={end_date}&timezone={timezone}")

    def get_license_dashboard(self, license_type: str, timezone: str = "America/Sao_Paulo") -> dict:
        return self._get("dashboard", f"dashboard/license?type={license_type}&timezone={timezone}")

    def get_agents_usage_overview(self) -> dict:
        return self._get("billing", "dashboard/agents-usage-overview")

    # ── Reports ───────────────────────────────────────────────────────────────

    def list_reports(self) -> dict:
        return self._get("report", "list")

    def schedule_report(self, begin_date: str, end_date: str, timezone: str = "America/Sao_Paulo", **params) -> dict:
        return self._post("report", f"scheduler?beginDate={begin_date}&endDate={end_date}&timezone={timezone}&lang={self.lang}", params)

    def get_report_download_link(self, report_id: str) -> dict:
        return self._get("report", f"downloadlink?reportId={report_id}")

    # ── Notifications ─────────────────────────────────────────────────────────

    def get_notifications(self, status: str = "all", total_days: int = 30, page: int = 1, page_size: int = 20) -> dict:
        return self._get("notification", f"all-notifications?status={status}&totalDays={total_days}&page={page}&pageSize={page_size}&lang={self.lang}")

    def get_unread_count(self) -> dict:
        return self._get("notification", "unread-notifications")

    def mark_all_read(self) -> dict:
        return self._post("notification", "mark-all-as-read?markAsReadByPeriod=false", {})

    def delete_notifications(self) -> dict:
        return self._delete("notification", "delete-notifications")

    # ── Alerts & Rules (coreregistry-api) ─────────────────────────────────────

    def get_alerts(self) -> dict:
        return self._get("registry", "alerts")

    def get_alert(self, alert_id: str) -> dict:
        return self._get("registry", f"alerts/{alert_id}")

    def toggle_alert(self, alert_id: str) -> dict:
        return self._post("registry", f"alerts/{alert_id}/toggle", {})

    def get_alert_executions(self, alert_id: str, page: int = 1, page_size: int = 20) -> dict:
        return self._get("registry", f"alerts/{alert_id}/executions?pageNumber={page}&pageSize={page_size}")

    def get_webhooks(self) -> dict:
        return self._get("registry", "webhooks")

    def get_webhook(self, webhook_id: str) -> dict:
        return self._get("registry", f"webhooks/{webhook_id}")

    # ── Billing ───────────────────────────────────────────────────────────────

    def get_active_plan(self) -> dict:
        return self._get("billing", "plan/active")

    def get_plan_parameters(self) -> dict:
        return self._get("billing", "plan/parameters")

    # ── Agent communication (agentcomm-api) ───────────────────────────────────

    def agentcomm_health(self) -> dict:
        """No auth required."""
        resp = requests.get(BASE_URLS["agentcomm"])
        return resp.json()

    # ── Locker ────────────────────────────────────────────────────────────────

    def get_locker_unlock_token(self) -> dict:
        return self._get("register", f"locker/unlock-token?lang={self.lang}")

    # ── HTTP helpers ──────────────────────────────────────────────────────────

    def _url(self, service: str, path: str) -> str:
        return BASE_URLS[service] + path

    def _get(self, service: str, path: str, params: dict = None) -> dict:
        resp = self.session.get(self._url(service, path), params=params)
        return resp.json()

    def _post(self, service: str, path: str, data: Any) -> dict:
        resp = self.session.post(self._url(service, path), json=data)
        return resp.json()

    def _put(self, service: str, path: str, data: Any) -> dict:
        resp = self.session.put(self._url(service, path), json=data)
        return resp.json()

    def _delete(self, service: str, path: str) -> dict:
        resp = self.session.delete(self._url(service, path))
        return resp.json()


if __name__ == "__main__":
    import json, sys

    if len(sys.argv) < 3:
        print("Usage: python client.py <username> <password> [method] [args...]")
        print("Example: python client.py admin@company.com pass123 get_me")
        sys.exit(1)

    client = XoneClient(sys.argv[1], sys.argv[2])
    print("Logging in...")
    result = client.login()
    print(f"Login: {result.get('message', 'ok')} | token={'yes' if client.token else 'no'}")

    if len(sys.argv) > 3:
        method = sys.argv[3]
        args = sys.argv[4:]
        fn = getattr(client, method, None)
        if fn:
            out = fn(*args)
            print(json.dumps(out, indent=2, ensure_ascii=False))
        else:
            print(f"Unknown method: {method}")
