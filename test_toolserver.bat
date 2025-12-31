echo off
REM Tool Server API Test Script (Windows)

set SERVER=http://localhost:8001
set TASK_ID=%TEMP%\mla_test_%RANDOM%

echo === Tool Server API Test ===
echo Task directory: %TASK_ID%
mkdir "%TASK_ID%" 2>nul

REM Test file write
echo Testing file_write...
curl -s -X POST "%SERVER%/api/tool/execute" -H "Content-Type: application/json" -d "{\"task_id\":\"%TASK_ID:\=/%\",\"tool_name\":\"file_write\",\"params\":{\"path\":\"test.txt\",\"content\":\"Hello World\"}}" | findstr /C:"success" >nul && echo Success || echo Failure

REM Test file read
echo Testing file_read...
curl -s -X POST "%SERVER%/api/tool/execute" -H "Content-Type: application/json" -d "{\"task_id\":\"%TASK_ID:\=/%\",\"tool_name\":\"file_read\",\"params\":{\"path\":\"test.txt\"}}" | findstr /C:"success" >nul && echo Success || echo Failure

REM Test directory listing
echo Testing dir_list...
curl -s -X POST "%SERVER%/api/tool/execute" -H "Content-Type: application/json" -d "{\"task_id\":\"%TASK_ID:\=/%\",\"tool_name\":\"dir_list\",\"params\":{\"path\":\".\"}}" | findstr /C:"success" >nul && echo Success || echo Failure

REM Test directory creation
echo Testing dir_create...
curl -s -X POST "%SERVER%/api/tool/execute" -H "Content-Type: application/json" -d "{\"task_id\":\"%TASK_ID:\=/%\",\"tool_name\":\"dir_create\",\"params\":{\"path\":\"testdir\"}}" | findstr /C:"success" >nul && echo Success || echo Failure

REM Test file move
echo Testing file_move...
curl -s -X POST "%SERVER%/api/tool/execute" -H "Content-Type: application/json" -d "{\"task_id\":\"%TASK_ID:\=/%\",\"tool_name\":\"file_move\",\"params\":{\"source\":\"test.txt\",\"destination\":\"testdir/test.txt\"}}" | findstr /C:"success" >nul && echo Success || echo Failure

REM Test Python code execution
echo Testing execute_code (Python)...
curl -s -X POST "%SERVER%/api/tool/execute" -H "Content-Type: application/json" -d "{\"task_id\":\"%TASK_ID:\=/%\",\"tool_name\":\"execute_code\",\"params\":{\"language\":\"python\",\"code\":\"print('Hello from Python')\"}}" | findstr /C:"success" >nul && echo Success || echo Failure

REM Test command execution
echo Testing execute_command...
curl -s -X POST "%SERVER%/api/tool/execute" -H "Content-Type: application/json" -d "{\"task_id\":\"%TASK_ID:\=/%\",\"tool_name\":\"execute_command\",\"params\":{\"command\":\"dir\"}}" | findstr /C:"success" >nul && echo Success || echo Failure

REM Test web search
echo Testing web_search...
curl -s -X POST "%SERVER%/api/tool/execute" -H "Content-Type: application/json" -d "{\"task_id\":\"%TASK_ID:\=/%\",\"tool_name\":\"web_search\",\"params\":{\"query\":\"Python\",\"max_results\":3,\"save_path\":\"search.md\"}}" | findstr /C:"success" >nul && echo Success || echo Failure

REM Test arXiv search
echo Testing arxiv_search...
curl -s -X POST "%SERVER%/api/tool/execute" -H "Content-Type: application/json" -d "{\"task_id\":\"%TASK_ID:\=/%\",\"tool_name\":\"arxiv_search\",\"params\":{\"query\":\"neural network\",\"max_results\":2,\"save_path\":\"arxiv.md\"}}" | findstr /C:"success" >nul && echo Success || echo Failure

REM Test Google Scholar search
echo Testing google_scholar_search...
curl -s -X POST "%SERVER%/api/tool/execute" -H "Content-Type: application/json" -d "{\"task_id\":\"%TASK_ID:\=/%\",\"tool_name\":\"google_scholar_search\",\"params\":{\"query\":\"machine learning\",\"pages\":1,\"save_path\":\"scholar.md\"}}" | findstr /C:"success" >nul && echo Success || echo Failure

REM Test webpage crawling
echo Testing crawl_page...
curl -s -X POST "%SERVER%/api/tool/execute" -H "Content-Type: application/json" -d "{\"task_id\":\"%TASK_ID:\=/%\",\"tool_name\":\"crawl_page\",\"params\":{\"url\":\"https://example.com\",\"save_path\":\"page.md\"}}" | findstr /C:"success" >nul && echo Success || echo Failure

REM Test file download
echo Testing file_download...
curl -s -X POST "%SERVER%/api/tool/execute" -H "Content-Type: application/json" -d "{\"task_id\":\"%TASK_ID:\=/%\",\"tool_name\":\"file_download\",\"params\":{\"url\":\"https://www.python.org/static/favicon.ico\",\"save_path\":\"favicon.ico\"}}" | findstr /C:"success" >nul && echo Success || echo Failure

REM Test pip installation
echo Testing pip_install...
curl -s -X POST "%SERVER%/api/tool/execute" -H "Content-Type: application/json" -d "{\"task_id\":\"%TASK_ID:\=/%\",\"tool_name\":\"pip_install\",\"params\":{\"packages\":[\"requests\"]}}" | findstr /C:"success" >nul && echo Success || echo Failure

REM Copy test PDF file
if exist test.pdf copy test.pdf "%TASK_ID%\test.pdf" >nul 2>&1

REM Test PDF document parsing
echo Testing parse_document...
curl -s -X POST "%SERVER%/api/tool/execute" -H "Content-Type: application/json" -d "{\"task_id\":\"%TASK_ID:\=/%\",\"tool_name\":\"parse_document\",\"params\":{\"path\":\"test.pdf\",\"save_path\":\"parsed.txt\"}}" | findstr /C:"success" >nul && echo Success || echo Failure

REM Test file deletion
echo Testing file_delete...
curl -s -X POST "%SERVER%/api/tool/execute" -H "Content-Type: application/json" -d "{\"task_id\":\"%TASK_ID:\=/%\",\"tool_name\":\"file_delete\",\"params\":{\"path\":\"testdir\"}}" | findstr /C:"success" >nul && echo Success || echo Failure

echo.
echo Test completed, cleaning up: rmdir /s /q "%TASK_ID%"
rmdir /s /q "%TASK_ID%" 2>nul

pause
