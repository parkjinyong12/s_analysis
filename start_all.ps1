# 백엔드(Flask) 실행
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd .; .\backend\venv\Scripts\Activate; python -m backend.app'

# 프론트엔드(Vue) 실행
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd frontend; npm run serve' 