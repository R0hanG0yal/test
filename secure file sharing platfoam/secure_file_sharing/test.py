import sqlite3
import urllib.request, urllib.parse, http.cookiejar

conn = sqlite3.connect("backend/secure_share.db")
conn.execute("INSERT OR IGNORE INTO files (id, owner_id, filename, original_name) VALUES (1, 1, 'mock.txt', 'mock.txt')")
conn.execute("INSERT OR IGNORE INTO access_requests (file_id, requester_email, status) VALUES (1, 'req@example.com', 'pending')")
conn.commit()
conn.close()

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
data = urllib.parse.urlencode({"email": "test@test.com", "password": "password"}).encode()
opener.open("http://127.0.0.1:5000/login", data)

try:
    resp = opener.open("http://127.0.0.1:5000/requests")
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
    if hasattr(e, "read"):
        print(e.read().decode())
