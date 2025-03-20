from zapv2 import ZAPv2
import time

# OWASP ZAP API URL'sini belirtin
zap = ZAPv2(apikey='tfu8u1o4834lnnt8ase8opk0rq', proxies={'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'})

target="https://jameskle.com/"
scan_id = zap.spider.scan(target)

# Wait for the spider to complete
while int(zap.spider.status(scan_id)) < 100:
    print(f"Spider progress: {zap.spider.status(scan_id)}%")
    time.sleep(5)

# Start the active scan
print("Starting active scan...")
zap.ascan.scan(target)

# Wait for the active scan to complete
# while int(zap.ascan.status()) < 100:
#     print(f"Active scan progress: {zap.ascan.status()}%")
#     time.sleep(5)

# Generate a report
report = zap.core.htmlreport()
with open("zap_report.html", "w") as f:
    f.write(report)
