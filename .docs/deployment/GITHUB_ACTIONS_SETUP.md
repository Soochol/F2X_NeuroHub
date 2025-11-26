# GitHub Actions CI/CD 설정 가이드

F2X NeuroHub MES의 GitHub Actions 기반 자동 배포 설정 가이드입니다.

## 개요

```
개발 PC                    GitHub                     배포 서버 (Windows Server)
┌─────────────┐           ┌─────────────┐            ┌─────────────────────────┐
│ git push    │──────────►│ Actions     │───명령────►│ Self-hosted Runner      │
│ main branch │           │ Workflow    │            │                         │
└─────────────┘           └─────────────┘            │ ► git pull              │
                                                     │ ► docker build          │
                                                     │ ► docker up             │
                                                     └─────────────────────────┘
```

main 브랜치에 push하면 자동으로 배포 서버에 배포됩니다.

## 사전 요구사항

### 배포 서버 (Windows Server)

| 항목 | 필수 | 용도 |
|------|------|------|
| Docker Desktop | ✅ | 컨테이너 실행 |
| Git | ✅ | 소스 코드 clone/pull |
| GitHub Actions Runner | ✅ | 자동 배포 수신 |

## 설정 단계

### 1. 배포 서버에 Docker Desktop 설치

1. [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop) 다운로드
2. 설치 후 재부팅
3. Docker Desktop 실행 및 로그인
4. Settings → General → "Start Docker Desktop when you log in" 체크

### 2. 배포 서버에 Git 설치

1. [Git for Windows](https://git-scm.com/download/win) 다운로드
2. 설치 (기본 옵션 사용)

### 3. Self-hosted Runner 설치

#### 3.1 GitHub에서 Runner 토큰 받기

1. GitHub 저장소 페이지로 이동
2. **Settings** → **Actions** → **Runners** 클릭
3. **New self-hosted runner** 버튼 클릭
4. Operating System: **Windows** 선택
5. Architecture: **x64** 선택
6. 표시되는 설치 명령어와 토큰을 메모

#### 3.2 배포 서버에서 Runner 설치

**PowerShell (관리자 권한)로 실행:**

```powershell
# 1. 폴더 생성
mkdir C:\actions-runner
cd C:\actions-runner

# 2. Runner 다운로드 (GitHub 페이지에서 표시된 URL 사용)
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-win-x64-2.321.0.zip -OutFile actions-runner-win-x64-2.321.0.zip

# 3. 압축 해제
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory("$PWD\actions-runner-win-x64-2.321.0.zip", "$PWD")

# 4. Runner 설정 (YOUR_TOKEN을 GitHub에서 받은 토큰으로 교체)
.\config.cmd --url https://github.com/YOUR_USERNAME/YOUR_REPO --token YOUR_TOKEN
```

설정 중 질문에 답변:
- **Enter the name of the runner group**: Enter (기본값)
- **Enter the name of runner**: Enter (기본값) 또는 원하는 이름
- **Enter any additional labels**: Enter (기본값)
- **Enter name of work folder**: Enter (기본값)
- **Would you like to run the runner as service?**: **Y**
- **User account to use for the service**: Enter (기본값: NT AUTHORITY\NETWORK SERVICE)

#### 3.3 PowerShell 실행 정책 설정

```powershell
# 관리자 권한 PowerShell에서 실행
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
```

#### 3.4 Docker 권한 설정

Runner 서비스가 Docker를 사용할 수 있도록 설정:

```powershell
# docker-users 그룹에 NETWORK SERVICE 추가
net localgroup docker-users "NT AUTHORITY\NETWORK SERVICE" /add

# Runner 서비스 재시작
Restart-Service "actions.runner.*"
```

또는 Runner를 관리자 계정으로 실행:

```powershell
# 서비스 제거 후 관리자 계정으로 재설치
cd C:\actions-runner
sc stop "actions.runner.YOUR_REPO.YOUR_RUNNER"
sc delete "actions.runner.YOUR_REPO.YOUR_RUNNER"

# 다시 설정
.\config.cmd --url https://github.com/YOUR_USERNAME/YOUR_REPO --token NEW_TOKEN

# 서비스 설치 시 관리자 계정 입력
# User account: .\Administrator (또는 관리자 계정)
```

### 4. 환경 변수 파일 생성

배포 서버의 프로젝트 폴더에 `.env.production` 파일 생성:

```powershell
cd C:\actions-runner\_work\F2X_NeuroHub\F2X_NeuroHub
copy .env.production.example .env.production
```

`.env.production` 파일 편집:

```env
# Database
POSTGRES_DB=f2x_neurohub_mes
POSTGRES_USER=postgres
POSTGRES_PASSWORD=강력한_비밀번호_입력

# Security (아래 명령으로 생성)
# python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=생성된_시크릿_키

# Application
DEBUG=false

# Network
HTTP_PORT=80
CORS_ORIGINS=["http://localhost","http://서버IP"]
```

### 5. Runner 상태 확인

GitHub 저장소 → Settings → Actions → Runners에서 Runner가 **Idle** (초록색) 상태인지 확인

## Workflow 파일 구조

`.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main
    paths-ignore:
      - '**.md'
      - '.gitignore'
      - 'neurohub_client/**'

  workflow_dispatch:  # 수동 배포 트리거

jobs:
  deploy:
    runs-on: self-hosted
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Check environment file
        # .env.production 파일 확인

      - name: Build Docker images
        # docker-compose build

      - name: Start services
        # docker-compose up -d

      - name: Health check
        # 서비스 상태 확인

      - name: Run database migrations
        # alembic upgrade head
```

## 배포 트리거

### 자동 배포

main 브랜치에 push하면 자동으로 배포가 시작됩니다:

```bash
git add .
git commit -m "feat: 새로운 기능 추가"
git push origin main
```

### 수동 배포

GitHub Actions 페이지에서 수동으로 배포 실행:

1. GitHub 저장소 → Actions 탭
2. "Deploy to Production" workflow 선택
3. "Run workflow" 버튼 클릭
4. Branch: main 선택 후 "Run workflow"

## 배포 제외 항목

다음 변경사항은 배포를 트리거하지 않습니다:

- `**.md` - 마크다운 문서
- `.gitignore`
- `neurohub_client/**` - PySide6 클라이언트 (별도 배포)

## 트러블슈팅

### Runner가 Offline 상태

```powershell
# 서비스 상태 확인
Get-Service *actions*

# 서비스 재시작
Restart-Service "actions.runner.*"
```

### Docker 권한 에러

```
error during connect: ... Access is denied.
```

해결:
```powershell
net localgroup docker-users "NT AUTHORITY\NETWORK SERVICE" /add
Restart-Service "actions.runner.*"
```

### PowerShell 스크립트 실행 에러

```
running scripts is disabled on this system
```

해결:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
```

### Health Check 실패

1. 컨테이너 상태 확인:
   ```powershell
   docker ps -a
   ```

2. 백엔드 로그 확인:
   ```powershell
   docker logs f2x-backend
   ```

3. Health 엔드포인트 직접 확인:
   ```powershell
   curl http://localhost/health
   ```

### 환경 변수 파일 없음

```
.env.production file not found!
```

해결: 배포 서버의 프로젝트 폴더에 `.env.production` 파일 생성

## 서비스 관리

배포 서버에서 직접 서비스 관리:

| 작업 | 명령어 |
|------|--------|
| 서비스 시작 | `deploy.bat start` |
| 서비스 중지 | `deploy.bat stop` |
| 서비스 재시작 | `deploy.bat restart` |
| 로그 확인 | `deploy.bat logs` |
| 백엔드 로그만 | `deploy.bat logs backend` |
| 서비스 상태 | `deploy.bat status` |

## 보안 고려사항

1. **`.env.production` 파일은 절대 Git에 커밋하지 마세요** (`.gitignore`에 포함됨)
2. SECRET_KEY는 충분히 긴 랜덤 문자열 사용
3. POSTGRES_PASSWORD는 강력한 비밀번호 사용
4. 프로덕션 환경에서는 DEBUG=false 유지
5. CORS_ORIGINS에 필요한 도메인만 추가

## 참고 링크

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [Self-hosted Runner 문서](https://docs.github.com/en/actions/hosting-your-own-runners)
- [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
