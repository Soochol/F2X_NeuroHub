"""
Hot Reload Preview System for PySide6/PyQt6

Automatically reload and preview your GUI app when files change.
Perfect for AI-assisted development with instant visual feedback.

Usage:
    python hot_reload_preview.py your_app.py
    
    # With visual debugger
    python hot_reload_preview.py your_app.py --debug
    
    # Watch multiple files
    python hot_reload_preview.py main.py ui/widgets.py --watch-dir ui/
"""

import sys
import importlib.util
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QFileSystemWatcher, QTimer
import traceback


class HotReloadManager:
    """핫 리로드 관리자"""
    
    def __init__(self, target_file, use_debugger=False, watch_dirs=None):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.target_file = Path(target_file).resolve()
        self.use_debugger = use_debugger
        self.watch_dirs = watch_dirs or []
        
        self.window = None
        self.debugger = None
        self.last_error = None
        
        # 파일 감시자 설정
        self.watcher = QFileSystemWatcher()
        self._setup_watcher()
        
        # 디바운스 타이머 (너무 빠른 연속 변경 방지)
        self.reload_timer = QTimer()
        self.reload_timer.setSingleShot(True)
        self.reload_timer.timeout.connect(self._do_reload)
        
        # 초기 로드
        self.reload_window()
    
    def _setup_watcher(self):
        """파일 감시자 설정"""
        # 타겟 파일 감시
        if self.target_file.exists():
            self.watcher.addPath(str(self.target_file))
        
        # 추가 디렉토리 감시
        for watch_dir in self.watch_dirs:
            dir_path = Path(watch_dir)
            if dir_path.exists() and dir_path.is_dir():
                self.watcher.addPath(str(dir_path))
                # 하위 Python 파일들도 감시
                for py_file in dir_path.rglob("*.py"):
                    self.watcher.addPath(str(py_file))
        
        # 변경 감지 시 디바운스 타이머 시작
        self.watcher.fileChanged.connect(self._on_file_changed)
        self.watcher.directoryChanged.connect(self._on_file_changed)
    
    def _on_file_changed(self, path):
        """파일 변경 감지"""
        print(f"\n📝 File changed: {Path(path).name}")
        
        # 디바운스: 500ms 대기
        self.reload_timer.start(500)
    
    def _do_reload(self):
        """실제 리로드 수행"""
        self.reload_window()
    
    def reload_window(self):
        """윈도우 재로드"""
        print(f"\n{'='*60}")
        print(f"🔄 Reloading: {self.target_file.name}")
        print(f"{'='*60}")
        
        # 기존 윈도우 닫기
        if self.window:
            try:
                self.window.close()
                self.window.deleteLater()
            except:
                pass
            self.window = None
        
        if self.debugger:
            try:
                self.debugger.close()
                self.debugger.deleteLater()
            except:
                pass
            self.debugger = None
        
        try:
            # 모듈 동적 로드
            spec = importlib.util.spec_from_file_location(
                f"target_module_{id(self)}", 
                self.target_file
            )
            
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load module from {self.target_file}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            
            # MainWindow 클래스 찾기
            if hasattr(module, 'MainWindow'):
                WindowClass = module.MainWindow
            elif hasattr(module, 'Window'):
                WindowClass = module.Window
            else:
                # 첫 번째 QMainWindow/QWidget 서브클래스 찾기
                from PySide6.QtWidgets import QMainWindow, QWidget
                WindowClass = None
                for name in dir(module):
                    obj = getattr(module, name)
                    if (isinstance(obj, type) and 
                        issubclass(obj, (QMainWindow, QWidget)) and 
                        obj not in (QMainWindow, QWidget)):
                        WindowClass = obj
                        break
                
                if WindowClass is None:
                    raise AttributeError(
                        "No MainWindow, Window, or QMainWindow/QWidget subclass found"
                    )
            
            # 윈도우 생성
            self.window = WindowClass()
            self.window.setWindowTitle(f"Preview: {self.target_file.name}")
            
            # 디버거 실행
            if self.use_debugger:
                from visual_debugger import launch_with_debugger
                self.debugger = launch_with_debugger(self.window)
            else:
                self.window.show()
            
            print(f"✅ Successfully loaded!")
            print(f"   Window: {WindowClass.__name__}")
            print(f"   Size: {self.window.width()}×{self.window.height()}")
            
            # 에러 초기화
            self.last_error = None
            
        except Exception as e:
            error_msg = f"❌ Error loading window:\n{traceback.format_exc()}"
            print(error_msg)
            self.last_error = error_msg
            
            # 에러 다이얼로그 표시
            self._show_error_dialog(str(e), traceback.format_exc())
        
        finally:
            # 파일 감시 재설정 (일부 에디터는 파일을 재생성함)
            self._rewatch_file()
    
    def _rewatch_file(self):
        """파일 감시 재설정"""
        watched_files = self.watcher.files()
        if str(self.target_file) not in watched_files:
            if self.target_file.exists():
                self.watcher.addPath(str(self.target_file))
    
    def _show_error_dialog(self, error, traceback_text):
        """에러 다이얼로그 표시"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
        
        dialog = QDialog()
        dialog.setWindowTitle("Reload Error")
        dialog.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 에러 메시지
        error_label = QTextEdit()
        error_label.setReadOnly(True)
        error_label.setPlainText(f"Error: {error}\n\n{traceback_text}")
        error_label.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ff6b6b;
                font-family: monospace;
                font-size: 10pt;
            }
        """)
        layout.addWidget(error_label)
        
        # 닫기 버튼
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.show()
    
    def run(self):
        """앱 실행"""
        print("\n" + "="*60)
        print("🔥 HOT RELOAD PREVIEW SYSTEM")
        print("="*60)
        print(f"Watching: {self.target_file}")
        if self.watch_dirs:
            print(f"Watch dirs: {', '.join(str(d) for d in self.watch_dirs)}")
        print(f"Debugger: {'Enabled' if self.use_debugger else 'Disabled'}")
        print("\n💡 Save your file to see changes instantly!")
        print("="*60 + "\n")
        
        return self.app.exec()


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Hot reload preview system for PySide6/PyQt6"
    )
    parser.add_argument(
        "target_file",
        help="Python file containing your GUI application"
    )
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Launch with visual debugger"
    )
    parser.add_argument(
        "-w", "--watch-dir",
        action="append",
        help="Additional directories to watch (can be specified multiple times)"
    )
    
    args = parser.parse_args()
    
    # 타겟 파일 확인
    target_file = Path(args.target_file)
    if not target_file.exists():
        print(f"❌ Error: File not found: {target_file}")
        sys.exit(1)
    
    # 핫 리로드 매니저 생성 및 실행
    manager = HotReloadManager(
        target_file,
        use_debugger=args.debug,
        watch_dirs=args.watch_dir
    )
    
    sys.exit(manager.run())


if __name__ == "__main__":
    main()
