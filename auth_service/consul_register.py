import requests

requests.put("http://localhost:8500/v1/agent/service/register", json={
    "ID":      "auth-service-1",
    "Name":    "auth-service",
    "Address": "127.0.0.1",
    "Port":    8000,
    "Check": {
        "TCP":      "127.0.0.1:8000",
        "Interval": "10s",
        "Timeout":  "3s",
    }
})
print("auth-service enregistré dans Consul")