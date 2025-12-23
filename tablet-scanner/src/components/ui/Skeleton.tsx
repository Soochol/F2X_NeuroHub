/**
 * Skeleton Loading Component
 *
 * 콘텐츠 로딩 중 표시되는 플레이스홀더
 * 시머 애니메이션으로 로딩 상태를 시각화
 */
import { cn } from '@/lib/cn';

export interface SkeletonProps {
  /** 너비 (Tailwind 클래스 또는 픽셀) */
  width?: string;
  /** 높이 (Tailwind 클래스 또는 픽셀) */
  height?: string;
  /** 둥근 모서리 정도 */
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'full';
  /** 원형 여부 */
  circle?: boolean;
  /** 추가 클래스 */
  className?: string;
  /** 애니메이션 활성화 */
  animate?: boolean;
  /** 인라인 스타일 */
  style?: React.CSSProperties;
}

const roundedClasses = {
  none: 'rounded-none',
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  full: 'rounded-full',
};

export const Skeleton: React.FC<SkeletonProps> = ({
  width,
  height,
  rounded = 'md',
  circle = false,
  className,
  animate = true,
  style: externalStyle,
}) => {
  const internalStyle: React.CSSProperties = {};

  // width/height가 Tailwind 클래스가 아닌 경우 인라인 스타일로
  if (width && !width.startsWith('w-')) {
    internalStyle.width = width;
  }
  if (height && !height.startsWith('h-')) {
    internalStyle.height = height;
  }

  return (
    <div
      className={cn(
        'bg-neutral-200',
        animate && 'animate-pulse',
        circle ? 'rounded-full' : roundedClasses[rounded],
        // Tailwind 클래스 형식일 경우 적용
        width?.startsWith('w-') && width,
        height?.startsWith('h-') && height,
        className
      )}
      style={{ ...internalStyle, ...externalStyle }}
    />
  );
};

/**
 * 텍스트 스켈레톤 - 한 줄 텍스트 플레이스홀더
 */
interface SkeletonTextProps {
  /** 줄 수 */
  lines?: number;
  /** 마지막 줄 너비 (%) */
  lastLineWidth?: number;
  /** 줄 간격 */
  spacing?: 'sm' | 'md' | 'lg';
  className?: string;
}

const spacingClasses = {
  sm: 'space-y-1',
  md: 'space-y-2',
  lg: 'space-y-3',
};

export const SkeletonText: React.FC<SkeletonTextProps> = ({
  lines = 3,
  lastLineWidth = 60,
  spacing = 'md',
  className,
}) => {
  return (
    <div className={cn(spacingClasses[spacing], className)}>
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          height="h-4"
          className={cn(
            index === lines - 1 && `w-[${lastLineWidth}%]`
          )}
          style={
            index === lines - 1
              ? { width: `${lastLineWidth}%` }
              : undefined
          }
        />
      ))}
    </div>
  );
};

/**
 * 카드 스켈레톤 - 카드 형태의 로딩 플레이스홀더
 */
interface SkeletonCardProps {
  /** 이미지 영역 표시 */
  hasImage?: boolean;
  /** 이미지 높이 */
  imageHeight?: string;
  /** 텍스트 줄 수 */
  lines?: number;
  className?: string;
}

export const SkeletonCard: React.FC<SkeletonCardProps> = ({
  hasImage = true,
  imageHeight = '120px',
  lines = 3,
  className,
}) => {
  return (
    <div
      className={cn(
        'bg-white rounded-xl p-4 shadow-sm',
        className
      )}
    >
      {hasImage && (
        <Skeleton
          height={imageHeight}
          rounded="lg"
          className="mb-4 w-full"
        />
      )}
      <SkeletonText lines={lines} />
    </div>
  );
};

/**
 * 아바타 스켈레톤
 */
interface SkeletonAvatarProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const avatarSizes = {
  sm: 'w-8 h-8',
  md: 'w-10 h-10',
  lg: 'w-12 h-12',
  xl: 'w-16 h-16',
};

export const SkeletonAvatar: React.FC<SkeletonAvatarProps> = ({
  size = 'md',
  className,
}) => {
  return (
    <Skeleton
      circle
      className={cn(avatarSizes[size], className)}
    />
  );
};

/**
 * 버튼 스켈레톤
 */
interface SkeletonButtonProps {
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  className?: string;
}

const buttonSizes = {
  sm: 'h-8 w-20',
  md: 'h-10 w-24',
  lg: 'h-12 w-32',
};

export const SkeletonButton: React.FC<SkeletonButtonProps> = ({
  size = 'md',
  fullWidth = false,
  className,
}) => {
  return (
    <Skeleton
      rounded="lg"
      className={cn(
        buttonSizes[size],
        fullWidth && 'w-full',
        className
      )}
    />
  );
};

/**
 * 리스트 아이템 스켈레톤
 */
interface SkeletonListItemProps {
  hasAvatar?: boolean;
  hasAction?: boolean;
  className?: string;
}

export const SkeletonListItem: React.FC<SkeletonListItemProps> = ({
  hasAvatar = true,
  hasAction = false,
  className,
}) => {
  return (
    <div
      className={cn(
        'flex items-center gap-3 p-3',
        className
      )}
    >
      {hasAvatar && <SkeletonAvatar size="md" />}
      <div className="flex-1 space-y-2">
        <Skeleton height="h-4" className="w-3/4" />
        <Skeleton height="h-3" className="w-1/2" />
      </div>
      {hasAction && <SkeletonButton size="sm" />}
    </div>
  );
};

/**
 * 프로세스 카드 스켈레톤 (Tablet Scanner 전용)
 */
export const SkeletonProcessCard: React.FC<{ className?: string }> = ({
  className,
}) => {
  return (
    <div
      className={cn(
        'bg-white rounded-xl p-4 shadow-sm border border-neutral-100',
        className
      )}
    >
      <div className="flex items-center gap-3 mb-3">
        <Skeleton circle className="w-10 h-10" />
        <div className="flex-1">
          <Skeleton height="h-5" className="w-24 mb-1" />
          <Skeleton height="h-3" className="w-16" />
        </div>
        <Skeleton rounded="full" className="w-16 h-6" />
      </div>
      <Skeleton height="h-2" rounded="full" className="w-full" />
    </div>
  );
};

/**
 * WIP 타임라인 스켈레톤 (Tablet Scanner 전용)
 */
export const SkeletonTimeline: React.FC<{
  items?: number;
  className?: string;
}> = ({ items = 4, className }) => {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: items }).map((_, index) => (
        <div key={index} className="flex items-center gap-3">
          <Skeleton circle className="w-8 h-8" />
          <div className="flex-1">
            <Skeleton height="h-4" className="w-32 mb-1" />
            <Skeleton height="h-3" className="w-20" />
          </div>
          <Skeleton rounded="md" className="w-12 h-5" />
        </div>
      ))}
    </div>
  );
};

export default Skeleton;
