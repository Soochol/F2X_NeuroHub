# 🌐 외부 망 접속 설정 가이드

## ✅ 설정 완료

### **1. Frontend (Vite)**
- ✅ `vite.config.ts`에 `host: true` 추가
- 외부에서 `http://<서버IP>:3000` 접속 가능

### **2. Backend (FastAPI)**
- ✅ 이미 `host="0.0.0.0"` 설정됨
- 외부에서 `http://<서버IP>:8000` 접속 가능

---

## 🔧 **접속 방법**

### **서버 IP 확인**
```powershell
# Windows에서 IP 확인
ipconfig

# 이더넷 또는 Wi-Fi 어댑터의 IPv4 주소 확인
# 예: 192.168.1.100
```

### **외부에서 접속**
```
Frontend: http://192.168.1.100:3000
Backend:  http://192.168.1.100:8000
```

---

## 🔥 **방화벽 설정**

### **Windows 방화벽 포트 열기**

**방법 1: PowerShell (관리자 권한)**
```powershell
# Frontend 포트 (3000) 열기
New-NetFirewallRule -DisplayName "Vite Dev Server" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow

# Backend 포트 (8000) 열기
New-NetFirewallRule -DisplayName "FastAPI Server" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

**방법 2: GUI**
1. Windows 방화벽 → 고급 설정
2. 인바운드 규칙 → 새 규칙
3. 포트 → TCP → 특정 로컬 포트: 3000, 8000
4. 연결 허용 → 완료

---

## 🚀 **서버 재시작**

Frontend 서버를 재시작해야 `host: true` 설정이 적용됩니다:

```powershell
# 현재 실행 중인 npm run dev 중지 (Ctrl+C)
# 다시 시작
cd frontend
npm run dev
```

**예상 출력**:
```
  ➜  Local:   http://localhost:3000/
  ➜  Network: http://192.168.1.100:3000/
```

---

## 📱 **테스트**

### **같은 네트워크의 다른 기기에서**
1. 스마트폰/태블릿을 같은 Wi-Fi에 연결
2. 브라우저에서 `http://192.168.1.100:3000` 접속
3. 로그인 페이지 확인

---

## ⚠️ **주의사항**

### **1. CORS 설정**
Backend는 이미 CORS가 설정되어 있어 외부 접속 가능:
```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **2. 보안**
- 개발 환경에서만 사용
- 프로덕션에서는 `allow_origins`를 특정 도메인으로 제한
- HTTPS 사용 권장

### **3. 네트워크**
- 같은 네트워크(Wi-Fi/LAN)에 있어야 접속 가능
- 공인 IP로 접속하려면 포트포워딩 필요

---

## 🎯 **프로덕션 배포**

개발 서버가 아닌 프로덕션 배포 시:

### **Frontend (Build)**
```bash
cd frontend
npm run build
# dist 폴더를 Nginx/Apache로 서빙
```

### **Backend (Production)**
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

또는 Gunicorn 사용:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## ✅ **체크리스트**

- [x] Frontend `vite.config.ts`에 `host: true` 추가
- [x] Backend `host="0.0.0.0"` 확인
- [ ] 방화벽 포트 3000, 8000 열기
- [ ] Frontend 서버 재시작
- [ ] 서버 IP 확인
- [ ] 외부 기기에서 접속 테스트
