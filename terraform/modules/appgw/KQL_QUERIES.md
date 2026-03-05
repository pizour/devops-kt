# Log Analytics KQL Queries for Application Gateway & WAF

Use these queries in **Azure Portal → Log Analytics Workspace → Logs**.

---

## 1. All Traffic (Access Logs)

Shows all requests hitting the Application Gateway with response codes.

```kql
AzureDiagnostics
| where ResourceType == "APPLICATIONGATEWAYS"
| where Category == "ApplicationGatewayAccessLog"
| project TimeGenerated, clientIP_s, requestUri_s, httpMethod_s, httpStatus_d, timeTaken_d, host_s, serverRouted_s, serverStatus_d
| sort by TimeGenerated desc
| take 100
```

---

## 2. HTTP Response Code Distribution

Summarize response codes over time to spot error trends.

```kql
AzureDiagnostics
| where ResourceType == "APPLICATIONGATEWAYS"
| where Category == "ApplicationGatewayAccessLog"
| summarize Count = count() by httpStatus_d, bin(TimeGenerated, 5m)
| sort by TimeGenerated desc
| render timechart
```

---

## 3. Top 10 Client IPs by Request Count

Identify the busiest clients.

```kql
AzureDiagnostics
| where ResourceType == "APPLICATIONGATEWAYS"
| where Category == "ApplicationGatewayAccessLog"
| summarize RequestCount = count() by clientIP_s
| top 10 by RequestCount desc
```

---

## 4. Requests per URL Path (API1 vs API2)

Compare traffic between /api1 and /api2 backends.

```kql
AzureDiagnostics
| where ResourceType == "APPLICATIONGATEWAYS"
| where Category == "ApplicationGatewayAccessLog"
| extend ApiPath = case(
    requestUri_s startswith "/api1", "/api1",
    requestUri_s startswith "/api2", "/api2",
    "other"
  )
| summarize Count = count() by ApiPath, bin(TimeGenerated, 5m)
| render timechart
```

---

## 5. Failed Requests (4xx and 5xx)

Show all client and server errors.

```kql
AzureDiagnostics
| where ResourceType == "APPLICATIONGATEWAYS"
| where Category == "ApplicationGatewayAccessLog"
| where httpStatus_d >= 400
| project TimeGenerated, clientIP_s, requestUri_s, httpMethod_s, httpStatus_d, serverStatus_d, serverRouted_s
| sort by TimeGenerated desc
| take 100
```

---

## 6. Backend Health (Server Response Codes)

Track what the backend (NVA) is returning.

```kql
AzureDiagnostics
| where ResourceType == "APPLICATIONGATEWAYS"
| where Category == "ApplicationGatewayAccessLog"
| summarize Count = count() by serverStatus_d, bin(TimeGenerated, 5m)
| render timechart
```

---

## 7. Average Response Time

Monitor latency over time.

```kql
AzureDiagnostics
| where ResourceType == "APPLICATIONGATEWAYS"
| where Category == "ApplicationGatewayAccessLog"
| summarize AvgTimeTaken = avg(timeTaken_d), P95TimeTaken = percentile(timeTaken_d, 95) by bin(TimeGenerated, 5m)
| render timechart
```

---

## 8. WAF Blocked Requests

All requests blocked by the WAF.

```kql
AzureDiagnostics
| where ResourceType == "APPLICATIONGATEWAYS"
| where Category == "ApplicationGatewayFirewallLog"
| where action_s == "Blocked"
| project TimeGenerated, clientIp_s, requestUri_s, ruleId_s, ruleGroup_s, message_s, action_s, details_message_s
| sort by TimeGenerated desc
| take 100
```

---

## 9. WAF Triggered Rules Summary

Most frequently triggered WAF rules.

```kql
AzureDiagnostics
| where ResourceType == "APPLICATIONGATEWAYS"
| where Category == "ApplicationGatewayFirewallLog"
| summarize HitCount = count() by ruleId_s, ruleGroup_s, action_s, message_s
| sort by HitCount desc
| take 20
```

---

## 10. WAF Events Over Time

WAF activity timeline (blocked vs matched).

```kql
AzureDiagnostics
| where ResourceType == "APPLICATIONGATEWAYS"
| where Category == "ApplicationGatewayFirewallLog"
| summarize Count = count() by action_s, bin(TimeGenerated, 15m)
| render timechart
```

---

## 11. Performance Logs

Application Gateway performance metrics.

```kql
AzureDiagnostics
| where ResourceType == "APPLICATIONGATEWAYS"
| where Category == "ApplicationGatewayPerformanceLog"
| project TimeGenerated, requestCount_d, healthyHostCount_d, unHealthyHostCount_d, throughput_d, latency_d
| sort by TimeGenerated desc
| take 100
```

---

## 12. Unhealthy Backend Instances

Detect when backend VMs fail health probes.

```kql
AzureDiagnostics
| where ResourceType == "APPLICATIONGATEWAYS"
| where Category == "ApplicationGatewayPerformanceLog"
| where unHealthyHostCount_d > 0
| project TimeGenerated, unHealthyHostCount_d, healthyHostCount_d, requestCount_d
| sort by TimeGenerated desc
```

---

## 13. Traffic Volume Over Time

Total request throughput.

```kql
AzureDiagnostics
| where ResourceType == "APPLICATIONGATEWAYS"
| where Category == "ApplicationGatewayAccessLog"
| summarize RequestCount = count() by bin(TimeGenerated, 5m)
| render timechart
```
