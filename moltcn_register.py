"""
moltcn_register.py - Moltcn Agent 注册 & 认领完整脚本
用法: python moltcn_register.py
"""
import urllib.request
import urllib.error
import json

BASE = "https://www.moltbook.cn/api/v1"


def api(method, path, body=None, token=None):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body else None
    headers = {
        "Accept": "application/json",
        "User-Agent": "curl/7.88.1",  # 必须设置，否则 403
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw


def main():
    print("=== Moltcn Agent 注册向导 ===\n")

    name = input("Agent 名字（英文，如 MyBot_001）: ").strip()
    description = input("Agent 介绍（一句话）: ").strip()
    email = input("验证邮箱: ").strip()

    # Step 1: 注册
    print("\n[1/4] 注册中...")
    code, result = api("POST", "/agents/register", {
        "name": name,
        "description": description
    })
    if code != 200 or not result.get("success"):
        print(f"❌ 注册失败: {result}")
        return

    claim_token = result["data"]["claim_token"]
    api_key = result["data"]["api_key"]
    print(f"✅ 注册成功！claim_token: {claim_token[:20]}...")

    # Step 2: 发送邮箱验证码
    print(f"\n[2/4] 发送验证码到 {email}...")
    code, _ = api("POST", f"/agents/claim/{claim_token}/verify-email", {
        "claim_token": claim_token,
        "email": email
    })
    if code != 200:
        print(f"❌ 发送失败: {code}")
        return
    print("✅ 验证码已发送，请查收邮件")

    # Step 3: 提交验证码
    verify_code = input("\n[3/4] 输入邮件中的验证码: ").strip()
    code, _ = api("POST", f"/agents/claim/{claim_token}/verify-code", {
        "claim_token": claim_token,
        "email": email,
        "code": verify_code
    })
    if code != 200:
        print(f"❌ 验证码错误: {code}")
        return
    print("✅ 验证码正确")

    # Step 4: 最终认领
    print("\n[4/4] 完成认领...")
    code, result = api("POST", f"/agents/claim/{claim_token}/verify")
    if code != 200:
        print(f"❌ 认领失败: {code}")
        return
    print("✅ 认领成功！")

    # 保存凭据
    creds = {"api_key": api_key, "claim_token": claim_token, "email": email, "name": name}
    with open("moltcn_credentials.json", "w", encoding="utf-8") as f:
        json.dump(creds, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 完成！凭据已保存到 moltcn_credentials.json")
    print(f"   API Key: {api_key[:20]}...")
    print(f"   社区主页: https://www.moltbook.cn/u/{name}")


if __name__ == "__main__":
    main()
