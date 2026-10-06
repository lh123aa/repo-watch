@echo off
rem ============================================================
rem  repo-watch 一键静默安装 (GBK/ANSI, 双击或 cmd 均可, 无需管理员)
rem    1. 安装唯一依赖 win10toast
rem    2. 把 GitHub Token 写入 repo_watch.config.json (可选, 参数传入)
rem    3. 生成 repo-watch.vbs 放进当前用户 Startup 目录 -> 开机自启
rem    4. 立即后台启动常驻进程 (pythonw, 无窗口)
rem  用法:
rem    setup.bat              静默安装 (不配 Token, 仅公开仓库)
rem    setup.bat ghp_xxxx    静默安装 + 写入 GitHub Token
rem ============================================================
setlocal EnableDelayedExpansion
set "ROOT=%~dp0"
set "SCRIPT=%ROOT%repo_watch.py"
set "CONFIG=%ROOT%repo_watch.config.json"
set "GENVBS=%ROOT%_gen_vbs.py"
set "SETUP_TOKEN=%ROOT%setup_token.py"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS=%STARTUP%\repo-watch.vbs"
set "TOKEN=%~1"

echo ============================================================
echo   repo-watch 静默安装开始
echo ============================================================

rem ---------- 0. 检查 Python ----------
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python。请先安装 Python 3.8+ 并加入 PATH。
    exit /b 1
)
for /f "delims=" %%v in ('python --version') do echo   检测 Python: %%v

rem ---------- 1. 安装依赖 ----------
echo   [1/4] 安装依赖 win10toast ...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install win10toast >nul 2>&1
if errorlevel 1 (
    python3 -m pip install win10toast >nul 2>&1
    if errorlevel 1 (
        echo [错误] 依赖安装失败, 请手动: python -m pip install win10toast
        exit /b 1
    )
)
echo   依赖安装完成。

rem ---------- 2. GitHub Token (可选, 经环境变量传入, 绝不交互) ----------
echo   [2/4] GitHub Token 配置
if defined TOKEN (
    echo   正在写入 %CONFIG% ...
    set "RW_CONFIG=%CONFIG%"
    set "RW_TOKEN=%TOKEN%"
    python "%SETUP_TOKEN%"
    if errorlevel 1 (
        echo [警告] 配置写入失败, 可稍后手动创建 %CONFIG% 填入 github_token
    ) else (
        echo   Token 已写入 %CONFIG%
    )
    set "RW_CONFIG="
    set "RW_TOKEN="
) else if exist "%CONFIG%" (
    echo   沿用已有配置 %CONFIG%
) else (
    echo   未提供 Token, 将仅监控公开仓库 (之后可 setup.bat ghp_xxx 补配)
)

rem ---------- 3. 开机自启: 生成 VBS (经环境变量传入, 避免中文 argv 被 cmd 弄坏) ----------
echo   [3/4] 配置开机自启 (Startup VBS, 无需管理员) ...
set "RW_ROOT=%ROOT%"
set "RW_SCRIPT=%SCRIPT%"
python "%GENVBS%"
if errorlevel 1 (
    echo [警告] VBS 生成失败 (Startup 目录不可写?)
) else (
    echo   VBS 已生成: %VBS%
)
set "RW_ROOT="
set "RW_SCRIPT="

rem ---------- 4. 立即后台启动 (若尚无 pythonw 后台实例) ----------
echo   [4/4] 启动后台常驻进程 ...
set "PW_CHECK=0"
tasklist /fi "imagename eq pythonw.exe" | findstr /i "pythonw" >nul
if not errorlevel 1 set "PW_CHECK=1"
if "%PW_CHECK%"=="1" (
    echo   检测到已有 pythonw 后台进程, 跳过重复启动。
) else (
    start "" /b pythonw "%SCRIPT%"
    echo   已启动后台进程。
)
rem ---------- 完成提示 ----------

echo.
echo ============================================================
echo   安装完成 (静默)!
echo   - 开机登录自动启动 (Startup VBS), 后台无窗口常驻
echo   - 首次扫描在开机 30 分钟后, 之后每 30 分钟一次
echo   - 有新版本时弹 Windows 系统通知, 逐个弹窗确认后才 git pull
echo   - 脏工作区(有未提交改动)自动跳过并警告
echo.
echo   手动运行: python "%SCRIPT%"
echo   检查一次: python "%SCRIPT%" --once
echo   列出仓库: python "%SCRIPT%" --list
echo   卸载:     del "%VBS%"  (并结束 pythonw 进程)
echo ============================================================
exit /b 0