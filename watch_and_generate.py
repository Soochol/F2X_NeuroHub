"""
워치 모드 + 자동 재생성 (Watch Mode + Auto Regeneration)

파일 변경을 감지하여 자동으로 코드를 재생성합니다.
- 요구사항 문서 변경 감지 (docs/requirements/)
- 설계 문서 변경 감지 (docs/design/)
- 5초 이내 자동 재생성
- Hot reload 지원

사용 예시:
    python watch_and_generate.py
    python watch_and_generate.py --module inventory
    python watch_and_generate.py --dirs docs/requirements/ docs/design/
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# watchdog 라이브러리가 필요합니다
# 설치: pip install watchdog
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("❌ watchdog 라이브러리가 필요합니다")
    print("   설치 명령: pip install watchdog")
    sys.exit(1)

# 프로젝트 내부 모듈
sys.path.insert(0, os.path.dirname(__file__))
from .neurohub.utils.incremental_builder import IncrementalBuilder
from .neurohub.cache.cache_manager import CacheManager


class RequirementsWatcher(FileSystemEventHandler):
    """요구사항 및 설계 문서 변경 감지 핸들러"""

    def __init__(self, incremental_builder: IncrementalBuilder,
                 cache_manager: CacheManager,
                 module_filter: str = None):
        """
        Args:
            incremental_builder: 증분 빌드 시스템
            cache_manager: 캐시 매니저
            module_filter: 특정 모듈만 감시 (None이면 전체)
        """
        self.builder = incremental_builder
        self.cache = cache_manager
        self.module_filter = module_filter
        self.debounce = {}  # 중복 이벤트 방지
        self.debounce_seconds = 1  # 1초 내 중복 이벤트 무시

    def on_modified(self, event):
        """파일 수정 이벤트 처리"""
        if event.is_directory:
            return

        file_path = event.src_path

        # markdown 파일만 감시
        if not file_path.endswith('.md'):
            return

        # 디버운스 체크
        now = time.time()
        if file_path in self.debounce:
            if (now - self.debounce[file_path]) < self.debounce_seconds:
                return
        self.debounce[file_path] = now

        # 파일 경로에서 모듈 추출
        module = self._extract_module(file_path)
        if module is None:
            return

        # 모듈 필터 적용
        if self.module_filter and module != self.module_filter:
            return

        # 변경 감지 및 재생성
        self._handle_file_change(file_path, module)

    def on_created(self, event):
        """파일 생성 이벤트 처리"""
        # 신규 파일은 즉시 처리
        if not event.is_directory and event.src_path.endswith('.md'):
            file_path = event.src_path
            module = self._extract_module(file_path)
            if module:
                print(f"\n📄 새 파일 감지: {file_path}")
                self._handle_file_change(file_path, module)

    def _extract_module(self, file_path: str) -> str:
        """
        파일 경로에서 모듈 이름 추출

        Args:
            file_path: 파일 경로

        Returns:
            모듈 이름 (예: 'inventory') 또는 None
        """
        path_parts = Path(file_path).parts

        # docs/requirements/modules/{module}/ 패턴
        if 'modules' in path_parts:
            try:
                module_index = path_parts.index('modules') + 1
                return path_parts[module_index]
            except IndexError:
                return None

        # docs/design/{module}/ 패턴
        if 'design' in path_parts:
            try:
                design_index = path_parts.index('design') + 1
                return path_parts[design_index]
            except IndexError:
                return None

        return None

    def _handle_file_change(self, file_path: str, module: str):
        """
        파일 변경 처리 및 재생성

        Args:
            file_path: 변경된 파일 경로
            module: 모듈 이름
        """
        print(f"\n{'='*60}")
        print(f"📝 변경 감지: {file_path}")
        print(f"   모듈: {module}")
        print(f"   시간: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}\n")

        try:
            # 1. 캐시 무효화
            self.cache.invalidate(file_path)

            # 2. 증분 빌드
            print(f"🔄 영향받는 코드 재생성 중...")
            start_time = time.time()

            result = self.builder.generate_if_changed(
                source_file=file_path,
                module=module,
                agent_executor=self._mock_agent_executor  # 실제 에이전트로 교체 필요
            )

            elapsed = time.time() - start_time

            # 3. 결과 출력
            if result['regenerated']:
                print(f"\n✅ 재생성 완료 ({elapsed:.1f}초)")
                print(f"   생성된 파일: {len(result.get('artifacts', []))}개")

                for artifact in result.get('artifacts', []):
                    print(f"      - {artifact}")

                # 4. 테스트 자동 실행 (옵션)
                if os.path.exists(f'tests/{module}/'):
                    self._run_tests(module)

            else:
                print(f"\n⏭️  변경 없음 또는 스킵")
                print(f"   이유: {result.get('reason', 'unknown')}")
                if 'time_saved' in result:
                    print(f"   절약된 시간: {result['time_saved']/60:.1f}분")

        except Exception as e:
            print(f"\n❌ 재생성 실패: {str(e)}")
            import traceback
            traceback.print_exc()

        print(f"\n{'='*60}")
        print(f"👀 변경 감시 중... (Ctrl+C로 종료)")
        print(f"{'='*60}\n")

    def _mock_agent_executor(self, source_file: str, module: str, affected_files: set):
        """
        모의 에이전트 실행 함수 (실제 구현 시 교체 필요)

        실제 구현에서는:
        1. 영향받는 파일 분석
        2. 필요한 에이전트 실행 (design, testing, implementation, verification)
        3. 생성된 파일 목록 반환
        """
        print(f"   [Mock] 에이전트 실행: {source_file}")
        print(f"   [Mock] 영향받는 파일: {len(affected_files)}개")

        # TODO: 실제 에이전트 호출로 교체
        # from .claude.agents import run_design_agent, run_implementation_agent

        # 예시 반환값
        return {
            'artifacts': [
                f'app/{module}/service.py',
                f'tests/{module}/test_service.py'
            ]
        }

    def _run_tests(self, module: str):
        """
        테스트 자동 실행

        Args:
            module: 모듈 이름
        """
        print(f"\n🧪 테스트 실행 중...")

        import subprocess
        try:
            result = subprocess.run(
                ['pytest', f'tests/{module}/', '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # 테스트 성공
                print(f"✅ 모든 테스트 통과!")

                # 통과한 테스트 수 추출
                import re
                match = re.search(r'(\d+) passed', result.stdout)
                if match:
                    passed = match.group(1)
                    print(f"   {passed}개 테스트 통과")

            else:
                # 테스트 실패
                print(f"❌ 테스트 실패")
                print(result.stdout)

        except subprocess.TimeoutExpired:
            print(f"⏱️  테스트 타임아웃 (60초 초과)")
        except FileNotFoundError:
            print(f"⚠️  pytest가 설치되지 않았습니다")
            print(f"   설치 명령: pip install pytest")
        except Exception as e:
            print(f"❌ 테스트 실행 실패: {str(e)}")


def main():
    """메인 실행 함수"""
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(
        description="파일 변경을 감지하여 자동으로 코드를 재생성합니다"
    )
    parser.add_argument(
        '--module',
        type=str,
        help='특정 모듈만 감시 (예: inventory)'
    )
    parser.add_argument(
        '--dirs',
        nargs='+',
        default=['docs/requirements/', 'docs/design/'],
        help='감시할 디렉토리 목록'
    )
    parser.add_argument(
        '--no-tests',
        action='store_true',
        help='테스트 자동 실행 비활성화'
    )

    args = parser.parse_args()

    # 시스템 초기화
    print("\n🚀 F2X NeuroHub 워치 모드 시작\n")

    builder = IncrementalBuilder()
    cache = CacheManager()

    # 캐시 통계 출력
    builder.print_cache_stats()
    cache.print_stats()

    # 파일 감시 시작
    event_handler = RequirementsWatcher(
        incremental_builder=builder,
        cache_manager=cache,
        module_filter=args.module
    )

    observer = Observer()

    # 감시 대상 디렉토리 등록
    for directory in args.dirs:
        if os.path.exists(directory):
            observer.schedule(event_handler, directory, recursive=True)
            print(f"👀 감시 중: {directory}")
        else:
            print(f"⚠️  디렉토리 없음: {directory}")

    observer.start()

    print(f"\n{'='*60}")
    print("✅ 워치 모드 활성화됨!")
    if args.module:
        print(f"   모듈 필터: {args.module}")
    print("   파일을 저장하면 자동으로 코드가 재생성됩니다")
    print("   Ctrl+C를 눌러 종료하세요")
    print(f"{'='*60}\n")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n⏹️  워치 모드 종료")
        observer.stop()

    observer.join()

    # 최종 통계 출력
    print("\n📊 최종 통계:")
    builder.print_cache_stats()
    cache.print_stats()


if __name__ == '__main__':
    main()
