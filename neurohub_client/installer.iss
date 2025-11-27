; F2X NeuroHub Client - Inno Setup Script
; 설치 프로그램 생성 스크립트

#define MyAppName "F2X NeuroHub Client"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "F2X"
#define MyAppExeName "NeuroHubClient.exe"

[Setup]
; 앱 식별자 (GUID 생성: https://www.guidgenerator.com/)
AppId={{F2X-NEUROHUB-CLIENT-2024}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; 설치 파일 출력 경로
OutputDir=dist\installer
OutputBaseFilename=NeuroHubClient_Setup_{#MyAppVersion}
; 압축 설정
Compression=lzma2/ultra64
SolidCompression=yes
; 아이콘
SetupIconFile=resources\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
; 권한
PrivilegesRequired=admin
; UI 설정
WizardStyle=modern
DisableProgramGroupPage=yes

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; PyInstaller로 빌드된 파일들
Source: "dist\application\NeuroHubClient\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; 기본 config.json 템플릿
Source: "config.template.json"; DestDir: "{app}"; DestName: "config.json"; Flags: onlyifdoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// 설치 전 이전 버전 제거 확인
function InitializeSetup(): Boolean;
var
  UninstallKey: String;
  UninstallString: String;
  ResultCode: Integer;
begin
  Result := True;
  UninstallKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1';

  if RegQueryStringValue(HKLM, UninstallKey, 'UninstallString', UninstallString) or
     RegQueryStringValue(HKCU, UninstallKey, 'UninstallString', UninstallString) then
  begin
    if MsgBox('이전 버전이 설치되어 있습니다. 제거하시겠습니까?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      Exec(RemoveQuotes(UninstallString), '/SILENT', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;
