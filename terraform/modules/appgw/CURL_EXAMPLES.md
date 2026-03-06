# Application Gateway API Curl Examples

Use these commands to test the APIs through Application Gateway on frontend ports `5000` and `5001`.

## Set IP Once

```bash
APPGW_IP="4.180.110.16"
```

## Basic API Tests

```bash
# API1 (frontend 5000)
curl -i "http://${APPGW_IP}:5000/"
curl -i "http://${APPGW_IP}:5000/status"
curl -i "http://${APPGW_IP}:5000/health"

# API2 (frontend 5001)
curl -i "http://${APPGW_IP}:5001/"
curl -i "http://${APPGW_IP}:5001/status"
curl -i "http://${APPGW_IP}:5001/health"
```

## Status Code Only

```bash
curl -s -o /dev/null -w "API1 / -> %{http_code}\n" "http://${APPGW_IP}:5000/"
curl -s -o /dev/null -w "API2 / -> %{http_code}\n" "http://${APPGW_IP}:5001/"
```

## Generate Traffic for Logs

```bash
for i in $(seq 1 20); do
  curl -s -o /dev/null -w "%{http_code} " "http://${APPGW_IP}:5000/"
done

echo

for i in $(seq 1 20); do
  curl -s -o /dev/null -w "%{http_code} " "http://${APPGW_IP}:5001/"
done

echo
```

## WAF Trigger Examples

These payloads are common OWASP signatures and should typically return `403` when WAF is in `Prevention` mode.

```bash
# SQLi-like payload
curl -i "http://${APPGW_IP}:5000/?id=1%27%20OR%20%271%27=%271"

# XSS-like payload
curl -i "http://${APPGW_IP}:5001/?q=%3Cscript%3Ealert(1)%3C/script%3E"

# Command-injection-like payload
curl -i "http://${APPGW_IP}:5000/?cmd=%3Bcat%20/etc/passwd"
```

## Expected Results

- Normal API calls: `200`
- WAF-trigger attempts: usually `403`
- If WAF is in `Detection` mode, requests may return `200` but still appear in WAF logs
