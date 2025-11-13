"""
문서 캐시 매니저 (Document Cache Manager)

FR/AC/Design 문서의 중복 읽기를 방지하고 파싱 결과를 캐싱합니다.
- 파일 변경 감지 (mtime 기반)
- 메모리 캐싱 + 디스크 영속화
- 에이전트 간 캐시 공유

사용 예시:
    cache = CacheManager()

    # FR 문서 캐싱
    fr_content = cache.get_or_load('docs/requirements/modules/inventory/FR-INV-001.md')

    # 파싱된 결과 캐싱
    parsed_data = cache.get_parsed('FR-INV-001')
    if not parsed_data:
        parsed_data = parse_fr_document(fr_content)
        cache.set_parsed('FR-INV-001', parsed_data)
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import pickle


class CacheManager:
    """문서 및 파싱 결과 캐시 매니저"""

    def __init__(self, cache_dir: str = '.neurohub/cache'):
        """
        Args:
            cache_dir: 캐시 디렉토리 경로
        """
        self.cache_dir = cache_dir
        self.memory_cache: Dict[str, Any] = {}
        self.metadata: Dict[str, Dict] = {}
        self._ensure_cache_dir()
        self._load_metadata()

    def _ensure_cache_dir(self):
        """캐시 디렉토리 생성"""
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(os.path.join(self.cache_dir, 'documents'), exist_ok=True)
        os.makedirs(os.path.join(self.cache_dir, 'parsed'), exist_ok=True)

    def _load_metadata(self):
        """메타데이터 로드"""
        metadata_file = os.path.join(self.cache_dir, 'metadata.json')
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                print(f"⚠️  메타데이터 로드 실패: {e}")
                self.metadata = {}
        else:
            self.metadata = {}

    def _save_metadata(self):
        """메타데이터 저장"""
        metadata_file = os.path.join(self.cache_dir, 'metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

    def _get_file_hash(self, file_path: str) -> str:
        """파일 해시 계산"""
        if not os.path.exists(file_path):
            return ''

        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def _get_cache_key(self, file_path: str) -> str:
        """캐시 키 생성"""
        # 파일 경로를 안전한 파일명으로 변환
        safe_name = file_path.replace('/', '_').replace('\\', '_').replace(':', '')
        return safe_name

    def is_cache_valid(self, file_path: str) -> bool:
        """
        캐시가 유효한지 확인 (파일 변경 여부)

        Args:
            file_path: 확인할 파일 경로

        Returns:
            True if 캐시 유효, False otherwise
        """
        cache_key = self._get_cache_key(file_path)

        if cache_key not in self.metadata:
            return False

        # 파일 해시 비교
        current_hash = self._get_file_hash(file_path)
        cached_hash = self.metadata[cache_key].get('file_hash', '')

        return current_hash == cached_hash

    def get_or_load(self, file_path: str) -> Optional[str]:
        """
        파일 내용 가져오기 (캐시 우선)

        Args:
            file_path: 읽을 파일 경로

        Returns:
            파일 내용 (문자열) 또는 None
        """
        # 1. 메모리 캐시 확인
        cache_key = self._get_cache_key(file_path)

        if cache_key in self.memory_cache and self.is_cache_valid(file_path):
            print(f"💾 메모리 캐시 히트: {file_path}")
            return self.memory_cache[cache_key]

        # 2. 디스크 캐시 확인
        cache_file = os.path.join(self.cache_dir, 'documents', f'{cache_key}.txt')

        if os.path.exists(cache_file) and self.is_cache_valid(file_path):
            print(f"💿 디스크 캐시 히트: {file_path}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.memory_cache[cache_key] = content
                return content

        # 3. 캐시 미스 - 파일 읽기
        if not os.path.exists(file_path):
            print(f"❌ 파일 없음: {file_path}")
            return None

        print(f"📖 파일 읽기: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 4. 캐시 저장
        self._cache_content(file_path, content)

        return content

    def _cache_content(self, file_path: str, content: str):
        """파일 내용을 캐시에 저장"""
        cache_key = self._get_cache_key(file_path)

        # 메모리 캐시
        self.memory_cache[cache_key] = content

        # 디스크 캐시
        cache_file = os.path.join(self.cache_dir, 'documents', f'{cache_key}.txt')
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # 메타데이터 업데이트
        self.metadata[cache_key] = {
            'original_path': file_path,
            'file_hash': self._get_file_hash(file_path),
            'cached_at': datetime.now().isoformat(),
            'file_size': len(content)
        }
        self._save_metadata()

    def get_parsed(self, document_id: str) -> Optional[Dict]:
        """
        파싱된 문서 가져오기

        Args:
            document_id: 문서 ID (예: 'FR-INV-001')

        Returns:
            파싱된 데이터 (딕셔너리) 또는 None
        """
        # 메모리 캐시
        mem_key = f'parsed_{document_id}'
        if mem_key in self.memory_cache:
            print(f"💾 파싱 캐시 히트 (메모리): {document_id}")
            return self.memory_cache[mem_key]

        # 디스크 캐시
        cache_file = os.path.join(self.cache_dir, 'parsed', f'{document_id}.pkl')
        if os.path.exists(cache_file):
            print(f"💿 파싱 캐시 히트 (디스크): {document_id}")
            try:
                with open(cache_file, 'rb') as f:
                    parsed_data = pickle.load(f)
                    self.memory_cache[mem_key] = parsed_data
                    return parsed_data
            except Exception as e:
                print(f"⚠️  파싱 캐시 로드 실패: {e}")
                return None

        return None

    def set_parsed(self, document_id: str, parsed_data: Dict):
        """
        파싱된 문서 저장

        Args:
            document_id: 문서 ID (예: 'FR-INV-001')
            parsed_data: 파싱된 데이터 (딕셔너리)
        """
        # 메모리 캐시
        mem_key = f'parsed_{document_id}'
        self.memory_cache[mem_key] = parsed_data

        # 디스크 캐시
        cache_file = os.path.join(self.cache_dir, 'parsed', f'{document_id}.pkl')
        with open(cache_file, 'wb') as f:
            pickle.dump(parsed_data, f)

        print(f"💾 파싱 결과 캐싱: {document_id}")

    def invalidate(self, file_path: Optional[str] = None):
        """
        캐시 무효화

        Args:
            file_path: 특정 파일만 무효화 (None이면 전체)
        """
        if file_path is None:
            # 전체 캐시 삭제
            self.memory_cache.clear()
            self.metadata.clear()
            print("🗑️  전체 캐시 삭제됨")
        else:
            # 특정 파일 캐시 삭제
            cache_key = self._get_cache_key(file_path)

            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]

            if cache_key in self.metadata:
                del self.metadata[cache_key]

            # 디스크 캐시 파일 삭제
            cache_file = os.path.join(self.cache_dir, 'documents', f'{cache_key}.txt')
            if os.path.exists(cache_file):
                os.remove(cache_file)

            print(f"🗑️  캐시 삭제: {file_path}")

        self._save_metadata()

    def get_cache_stats(self) -> Dict:
        """
        캐시 통계 정보

        Returns:
            {
                'memory_cache_size': int,
                'disk_cache_size': int,
                'total_cached_files': int,
                'total_cache_size_mb': float
            }
        """
        # 메모리 캐시 크기 (대략적)
        memory_size = sum(
            len(str(v)) if isinstance(v, str) else len(str(v))
            for v in self.memory_cache.values()
        )

        # 디스크 캐시 크기
        disk_size = 0
        for cache_type in ['documents', 'parsed']:
            cache_path = os.path.join(self.cache_dir, cache_type)
            if os.path.exists(cache_path):
                for file in os.listdir(cache_path):
                    file_path = os.path.join(cache_path, file)
                    if os.path.isfile(file_path):
                        disk_size += os.path.getsize(file_path)

        return {
            'memory_cache_items': len(self.memory_cache),
            'disk_cached_files': len(self.metadata),
            'memory_size_mb': memory_size / (1024 * 1024),
            'disk_size_mb': disk_size / (1024 * 1024),
            'total_size_mb': (memory_size + disk_size) / (1024 * 1024)
        }

    def print_stats(self):
        """캐시 통계 출력"""
        stats = self.get_cache_stats()
        print("\n📊 캐시 통계")
        print(f"   메모리 캐시: {stats['memory_cache_items']}개 항목")
        print(f"   디스크 캐시: {stats['disk_cached_files']}개 파일")
        print(f"   메모리 사용: {stats['memory_size_mb']:.2f} MB")
        print(f"   디스크 사용: {stats['disk_size_mb']:.2f} MB")
        print(f"   총 캐시 크기: {stats['total_size_mb']:.2f} MB\n")

    def warm_up(self, file_patterns: list):
        """
        캐시 예열 (자주 사용되는 파일들을 미리 로드)

        Args:
            file_patterns: 파일 패턴 목록 (예: ['docs/requirements/**/*.md'])
        """
        from glob import glob

        print("🔥 캐시 예열 중...")
        loaded_count = 0

        for pattern in file_patterns:
            files = glob(pattern, recursive=True)
            for file_path in files:
                if os.path.isfile(file_path):
                    self.get_or_load(file_path)
                    loaded_count += 1

        print(f"✅ {loaded_count}개 파일 캐싱 완료\n")


# 사용 예시
if __name__ == '__main__':
    # 캐시 매니저 초기화
    cache = CacheManager()

    # 캐시 통계 출력
    cache.print_stats()

    # 예시: FR 문서 캐싱
    fr_file = 'docs/requirements/modules/inventory/FR-INV-001.md'
    if os.path.exists(fr_file):
        content = cache.get_or_load(fr_file)
        if content:
            print(f"FR 문서 길이: {len(content)} 문자")

            # 파싱된 결과 캐싱 예시
            parsed_data = {
                'id': 'FR-INV-001',
                'title': '재고 조회 기능',
                'requirements': ['...']
            }
            cache.set_parsed('FR-INV-001', parsed_data)

            # 파싱 결과 재사용
            cached_parsed = cache.get_parsed('FR-INV-001')
            print(f"파싱 결과: {cached_parsed['title']}")

    # 캐시 예열 예시
    # cache.warm_up([
    #     'docs/requirements/modules/**/*.md',
    #     'docs/design/**/*.md'
    # ])

    # 캐시 통계 출력
    cache.print_stats()
