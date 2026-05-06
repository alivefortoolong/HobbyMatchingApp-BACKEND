import requests
requests.put("http://localhost:8500/v1/agent/service/register", json={
    "ID":      "notification-service-1",
    "Name":    "notification-service",
    "Address": "127.0.0.1",
    "Port":    8003,
    "Check": {
        "TCP":      "127.0.0.1:8003",
        "Interval": "10s",
        "Timeout":  "3s",
    }
})
print("notification-service enregistre dans Consul")
