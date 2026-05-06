import requests
requests.put("http://localhost:8500/v1/agent/service/register", json={
    "ID":      "matching-service-2",
    "Name":    "matching-service",
    "Address": "127.0.0.1",
    "Port":    8012,
    "Check": {
        "TCP":      "127.0.0.1:8012",
        "Interval": "10s",
        "Timeout":  "3s",
    }
})
print("matching-service-2 enregistre dans Consul")
