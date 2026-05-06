import requests
requests.put("http://localhost:8500/v1/agent/service/register", json={
    "ID":      "user-service-1",
    "Name":    "user-service",
    "Address": "127.0.0.1",
    "Port":    8001,
    "Check": {
        "TCP":      "127.0.0.1:8001",
        "Interval": "10s",
        "Timeout":  "3s",
    }
})
print("user-service enregistre dans Consul")
