/**
 * Page Container Component
 *
 * Responsive page wrapper with safe area support
 */
import { cn } from '@/lib/cn';

export interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
  noPadding?: boolean;
}

export const PageContainer: React.FC<PageContainerProps> = ({
  children,
  className,
  noPadding = false,
}) => {
  return (
    <div
      className={cn(
        'min-h-full w-full mx-auto',
        'max-w-[480px] sm:max-w-[540px] md:max-w-[720px]',
        'landscape:md:max-w-[900px]',
        'bg-neutral-50',
        'safe-area-inset',
        !noPadding && 'px-4 py-4',
        className
      )}
    >
      {children}
    </div>
  );
};
