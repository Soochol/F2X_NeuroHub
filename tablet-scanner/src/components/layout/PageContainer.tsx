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
        'bg-transparent',
        'safe-area-inset',
        !noPadding && 'px-6 py-6 lg:px-10 lg:py-8',
        className
      )}
    >
      {children}
    </div>
  );
};
