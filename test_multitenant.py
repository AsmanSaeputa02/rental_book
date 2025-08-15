#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-tenant Django API Test Suite (ปรับให้ตรงกับระบบของคุณแล้ว)
- Public superadmin login: /book_project/api/admin/login/ (fields: access, refresh, tenants)
- Tenant login:           /book_project/api/auth/login/  (fields: access, refresh)
- Book list per tenant:   /book_project/api/book/
- Cross-tenant create:    /book_project/api/admin/book/create-in-tenant/
"""

import requests
import time
from typing import Dict, Optional

class MultiTenantTester:
    def __init__(self):
        # ---- Base URLs ----
        self.public_base = "http://localhost:8003"
        self.tenant_a = "http://branch-a.localhost:8003"
        self.tenant_b = "http://branch-b.localhost:8003"

        # ---- Credentials (ตรงกับที่คุณใช้อยู่) ----
        self.super_email = "superadmin@example.com"
        self.super_pass = "P@ssw0rdasman"

        self.a_email = "owner@branch-a.com"
        self.a_pass  = "passA"

        self.b_email = "owner@branch-b.com"
        self.b_pass  = "passB"

        # Tokens
        self.super_token = None
        self.a_token = None
        self.b_token = None

        self.results = []

    # ---------- Utils ----------
    def log(self, msg: str, status: str = "INFO"):
        ts = time.strftime("%H:%M:%S")
        print(f"[{ts}] {status}: {msg}")
        self.results.append({"time": ts, "status": status, "message": msg})

    def req(self, method: str, url: str, headers: Dict = None, json: Dict = None, timeout=10) -> Optional[requests.Response]:
        try:
            method = method.upper()
            if method == "GET":
                return requests.get(url, headers=headers, timeout=timeout)
            if method == "POST":
                return requests.post(url, headers=headers, json=json, timeout=timeout)
            raise ValueError(f"Unsupported method {method}")
        except requests.RequestException as e:
            self.log(f"Request error @ {url}: {e}", "ERROR")
            return None

    # ---------- Tests ----------
    def test_public_login(self) -> bool:
        self.log("🔑 Testing Public Superadmin Login", "TEST")
        url = f"{self.public_base}/book_project/api/admin/login/"
        payload = {"email": self.super_email, "password": self.super_pass}
        r = self.req("POST", url, json=payload)
        if not r:
            self.log("❌ No response", "FAIL")
            return False
        if r.status_code != 200:
            self.log(f"❌ HTTP {r.status_code}: {r.text[:300]}", "FAIL")
            return False
        try:
            data = r.json()
        except ValueError:
            self.log("❌ Response is not JSON", "FAIL")
            return False

        token = data.get("access")  # field name is 'access'
        if not token:
            self.log("❌ Missing 'access' in response", "FAIL")
            return False

        self.super_token = token
        tenants = [t.get("schema_name") for t in data.get("tenants", [])]
        self.log(f"✅ Public login OK. Tenants: {tenants}", "PASS")
        return True

    def test_tenant_login(self, name: str, base_url: str, email: str, password: str) -> Optional[str]:
        self.log(f"🔑 Testing {name} Login", "TEST")
        url = f"{base_url}/book_project/api/auth/login/"
        r = self.req("POST", url, json={"email": email, "password": password})
        if not r:
            self.log("❌ No response", "FAIL"); return None
        if r.status_code != 200:
            self.log(f"❌ HTTP {r.status_code}: {r.text[:300]}", "FAIL"); return None
        try:
            data = r.json()
        except ValueError:
            self.log("❌ Not JSON", "FAIL"); return None

        token = data.get("access")
        if not token:
            self.log("❌ Missing 'access' in response", "FAIL"); return None
        self.log(f"✅ {name} login OK", "PASS")
        return token

    def test_cross_tenant_create(self):
        if not self.super_token:
            self.log("⏭️ Skipping cross-tenant create (no super token)", "SKIP"); return
        self.log("📚 Testing Superadmin Cross-Tenant Book Creation", "TEST")

        url = f"{self.public_base}/book_project/api/admin/book/create-in-tenant/"
        headers = {"Authorization": f"Bearer {self.super_token}"}

        cases = [
            ("branch_a", {"title": "Clean Code", "author": "Robert C. Martin", "isbn": "9780132350884", "available_count": 3}),
            ("branch_b", {"title": "Design Patterns", "author": "GoF", "isbn": "9780201633610", "available_count": 2}),
        ]
        for schema, data in cases:
            r = self.req("POST", url, headers=headers, json={"schema_name": schema, "data": data})
            if r and r.status_code in (200, 201):
                self.log(f"✅ Created book in {schema}", "PASS")
            else:
                code = r.status_code if r else "noresp"
                txt = (r.text[:300] if r and r.text else "")
                self.log(f"❌ Failed to create in {schema} (HTTP {code}) {txt}", "FAIL")

    def test_tenant_books(self, name: str, base_url: str, token: str):
        if not token:
            self.log(f"⏭️ Skip {name} /book/ (no token)", "SKIP"); return

        self.log(f"📖 Testing {name} /api/book/", "TEST")
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        url = f"{base_url}/book_project/api/book/"
        r = self.req("GET", url, headers=headers)
        if not r:
            self.log("❌ No response", "FAIL"); return
        if r.status_code != 200:
            self.log(f"❌ HTTP {r.status_code}: {r.text[:300]}", "FAIL"); return
        try:
            data = r.json()
        except ValueError:
            self.log("❌ Not JSON", "FAIL"); return

        if isinstance(data, list):
            self.log(f"✅ {name} books OK (count={len(data)})", "PASS")
            for b in data[:3]:
                self.log(f"   - {b.get('title','(no title)')} by {b.get('author','')}")
        else:
            self.log(f"✅ {name} books OK (non-list JSON)", "PASS")

    def test_whoami(self):
        self.log("🏠 Testing /whoami/", "TEST")
        targets = [
            ("Public", f"{self.public_base}/book_project/whoami/"),
            ("Tenant A", f"{self.tenant_a}/book_project/whoami/"),
            ("Tenant B", f"{self.tenant_b}/book_project/whoami/"),
        ]
        for name, url in targets:
            r = self.req("GET", url)
            if not r:
                self.log(f"❌ {name} whoami no response", "FAIL"); continue
            if r.status_code != 200:
                self.log(f"❌ {name} whoami HTTP {r.status_code}", "FAIL"); continue
            try:
                j = r.json()
                schema = j.get("current_schema", "unknown")
                self.log(f"✅ {name} whoami: {schema}", "PASS")
            except ValueError:
                self.log(f"❌ {name} whoami not JSON", "FAIL")

    def test_swagger(self):
        self.log("📋 Testing Swagger UI", "TEST")
        for name, base in [("Public", self.public_base), ("Tenant A", self.tenant_a), ("Tenant B", self.tenant_b)]:
            url = f"{base}/book_project/admin/swagger/"
            r = self.req("GET", url)
            if r and r.status_code == 200:
                self.log(f"✅ {name} swagger OK", "PASS")
            else:
                self.log(f"❌ {name} swagger NG (HTTP {r.status_code if r else 'noresp'})", "FAIL")

    def run(self):
        self.log("🚀 Starting Multi-tenant API Test Suite", "START")
        self.log("=" * 60)

        ok_pub = self.test_public_login()

        self.a_token = self.test_tenant_login("Tenant A", self.tenant_a, self.a_email, self.a_pass)
        self.b_token = self.test_tenant_login("Tenant B", self.tenant_b, self.b_email, self.b_pass)

        if ok_pub:
            self.test_cross_tenant_create()

        self.test_tenant_books("Tenant A", self.tenant_a, self.a_token)
        self.test_tenant_books("Tenant B", self.tenant_b, self.b_token)

        self.test_whoami()
        self.test_swagger()

        self.summary()

    def summary(self):
        self.log("=" * 60)
        self.log("📊 TEST SUMMARY", "SUMMARY")
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])
        skipped = len([r for r in self.results if r["status"] == "SKIP"])
        self.log(f"✅ PASSED: {passed}")
        self.log(f"❌ FAILED: {failed}")
        self.log(f"⏭️  SKIPPED: {skipped}")
        if failed == 0:
            self.log("🎉 ALL TESTS PASSED!", "SUCCESS")
        else:
            self.log("⚠️  Some tests failed. ดู log ข้างบนเพื่อไล่แก้", "WARNING")
            self.log("🔧 QUICK CHECK:")
            self.log("  - /etc/hosts มี: 127.0.0.1 branch-a.localhost branch-b.localhost")
            self.log("  - ALLOWED_HOSTS ครบ: localhost, branch-a.localhost, branch-b.localhost")
            self.log("  - seed_tenants แล้ว และสร้าง tenant admin เรียบร้อย")
            self.log("  - server รันที่ :8003")

def main():
    print("🏢 Multi-tenant Django API Tester")
    print("=" * 60)
    time.sleep(1)
    MultiTenantTester().run()

if __name__ == "__main__":
    main()
