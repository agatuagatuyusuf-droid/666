#property strict

// MT4 状态上报 EA 模板
// 使用方式：
// 1) 设置 ManagerUrl 与 InstanceId
// 2) 在 MT4 -> Tools -> Options -> Expert Advisors 中允许 WebRequest，并加入 ManagerUrl

input string ManagerUrl = "http://127.0.0.1:8000";
input int InstanceId = 1;
input int ReportIntervalSec = 5;
input string EaStatus = "active";

int OnInit()
{
   EventSetTimer(ReportIntervalSec);
   Print("MT4StatusReporter initialized. instance_id=", InstanceId);
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{
   EventKillTimer();
}

void OnTimer()
{
   string url = ManagerUrl + "/api/report/status";

   double balance = AccountBalance();
   double equity = AccountEquity();
   int account = AccountNumber();

   string payload = "{";
   payload += "\"instance_id\":" + IntegerToString(InstanceId) + ",";
   payload += "\"running\":true,";
   payload += "\"account_id\":\"" + IntegerToString(account) + "\",";
   payload += "\"account_balance\":" + DoubleToString(balance, 2) + ",";
   payload += "\"equity\":" + DoubleToString(equity, 2) + ",";
   payload += "\"ea_status\":\"" + EaStatus + "\"";
   payload += "}";

   char post[];
   StringToCharArray(payload, post, 0, WHOLE_ARRAY, CP_UTF8);

   char result[];
   string headers = "Content-Type: application/json\r\n";
   string response_headers;

   ResetLastError();
   int timeout = 5000;
   int code = WebRequest("POST", url, headers, timeout, post, result, response_headers);

   if(code == -1)
   {
      Print("Status report failed, error=", GetLastError());
      return;
   }

   Print("Status report code=", code);
}
