/**
 * Extracted component styles for consistent styling across the application
 * Uses CSS custom properties for theme support
 */

// ============================================================================
// TABLE STYLES
// ============================================================================

export const tableStyles = {
  headerRow: {
    borderBottom: '2px solid var(--color-border-strong)',
    backgroundColor: 'var(--color-table-header-bg)',
  } as const,

  headerCell: {
    padding: '12px',
    textAlign: 'left' as const,
    fontWeight: '600',
    color: 'var(--color-text-primary)',
  } as const,

  headerCellCenter: {
    padding: '12px',
    textAlign: 'center' as const,
    fontWeight: '600',
    color: 'var(--color-text-primary)',
  } as const,

  bodyRow: (index: number) => ({
    borderBottom: '1px solid var(--color-table-border)',
    backgroundColor: index % 2 === 0 ? 'var(--color-table-row-bg)' : 'var(--color-bg-secondary)',
    transition: 'background-color var(--transition-fast)',
  }),

  bodyRowHover: {
    backgroundColor: 'var(--color-table-row-hover)',
  } as const,

  bodyCell: {
    padding: '12px',
    color: 'var(--color-text-primary)',
  } as const,

  bodyCellCenter: {
    padding: '12px',
    textAlign: 'center' as const,
    color: 'var(--color-text-primary)',
  } as const,
};

// ============================================================================
// BADGE/STATUS STYLES
// ============================================================================

export const badgeStyles = {
  base: {
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '500',
  } as const,

  success: {
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '500',
    backgroundColor: 'var(--color-badge-success-bg)',
    color: 'var(--color-success)',
  } as const,

  error: {
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '500',
    backgroundColor: 'var(--color-badge-error-bg)',
    color: 'var(--color-error)',
  } as const,

  warning: {
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '500',
    backgroundColor: 'var(--color-badge-warning-bg)',
    color: 'var(--color-warning)',
  } as const,

  info: {
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '500',
    backgroundColor: 'var(--color-badge-info-bg)',
    color: 'var(--color-info)',
  } as const,
};

// ============================================================================
// LAYOUT STYLES
// ============================================================================

export const layoutStyles = {
  flexBetween: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  } as const,

  flexCenter: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  } as const,

  flexEnd: {
    display: 'flex',
    justifyContent: 'flex-end',
    alignItems: 'center',
  } as const,

  gridAutoFit: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
  } as const,

  gridAutoFitLarge: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
  } as const,
};

// ============================================================================
// TYPOGRAPHY STYLES
// ============================================================================

export const typographyStyles = {
  h1: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: 'var(--color-text-primary)',
  } as const,

  h2: {
    fontSize: '18px',
    fontWeight: '600',
    color: 'var(--color-text-primary)',
  } as const,

  label: {
    display: 'block',
    marginBottom: '5px',
    fontWeight: '500',
    color: 'var(--color-text-primary)',
    fontSize: '14px',
  } as const,

  body: {
    fontSize: '14px',
    color: 'var(--color-text-primary)',
  } as const,

  secondary: {
    fontSize: '12px',
    color: 'var(--color-text-secondary)',
  } as const,
};

// ============================================================================
// CONTAINER STYLES
// ============================================================================

export const containerStyles = {
  loadingContainer: {
    textAlign: 'center' as const,
    padding: '40px',
    color: 'var(--color-text-secondary)',
  } as const,

  errorContainer: {
    textAlign: 'center' as const,
    padding: '40px',
    color: 'var(--color-error)',
  } as const,

  formGroup: {
    marginBottom: '15px',
  } as const,

  formGroupLarge: {
    marginBottom: '20px',
  } as const,
};

// ============================================================================
// FORM STYLES
// ============================================================================

export const formStyles = {
  input: {
    width: '100%',
    padding: '10px',
    border: '1px solid var(--color-input-border)',
    borderRadius: 'var(--radius-base)',
    fontSize: '14px',
    boxSizing: 'border-box' as const,
    backgroundColor: 'var(--color-input-bg)',
    color: 'var(--color-text-primary)',
    transition: 'border-color var(--transition-fast)',
  } as const,

  inputError: {
    width: '100%',
    padding: '10px',
    border: '1px solid var(--color-error)',
    borderRadius: 'var(--radius-base)',
    fontSize: '14px',
    boxSizing: 'border-box' as const,
    backgroundColor: 'var(--color-input-bg)',
    color: 'var(--color-text-primary)',
  } as const,

  inputFocus: {
    borderColor: 'var(--color-input-focus-border)',
    outline: 'none',
  } as const,

  modal: {
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'var(--color-bg-overlay)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  } as const,

  modalContent: {
    backgroundColor: 'var(--color-modal-bg)',
    border: '1px solid var(--color-modal-border)',
    borderRadius: 'var(--radius-lg)',
    display: 'flex',
    flexDirection: 'column' as const,
    overflow: 'hidden',
    boxShadow: 'var(--shadow-xl)',
  } as const,
};

// ============================================================================
// CARD STYLES
// ============================================================================

export const cardStyles = {
  base: {
    backgroundColor: 'var(--color-card-bg)',
    border: '1px solid var(--color-card-border)',
    borderRadius: 'var(--radius-lg)',
    padding: '24px',
    boxShadow: 'var(--shadow-base)',
  } as const,

  elevated: {
    backgroundColor: 'var(--color-bg-elevated)',
    border: '1px solid var(--color-border-strong)',
    borderRadius: 'var(--radius-lg)',
    padding: '24px',
    boxShadow: 'var(--shadow-md)',
  } as const,
};

// ============================================================================
// BUTTON STYLES
// ============================================================================

export const buttonStyles = {
  primary: {
    backgroundColor: 'var(--color-brand-400)',
    color: 'var(--color-text-inverse)',
    border: 'none',
    borderRadius: 'var(--radius-base)',
    padding: '8px 16px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'background-color var(--transition-fast)',
  } as const,

  primaryHover: {
    backgroundColor: 'var(--color-brand-500)',
  } as const,

  secondary: {
    backgroundColor: 'transparent',
    color: 'var(--color-text-primary)',
    border: '1px solid var(--color-border-strong)',
    borderRadius: 'var(--radius-base)',
    padding: '8px 16px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all var(--transition-fast)',
  } as const,

  secondaryHover: {
    backgroundColor: 'var(--color-bg-tertiary)',
  } as const,

  danger: {
    backgroundColor: 'var(--color-error)',
    color: 'var(--color-text-inverse)',
    border: 'none',
    borderRadius: 'var(--radius-base)',
    padding: '8px 16px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'background-color var(--transition-fast)',
  } as const,

  dangerHover: {
    backgroundColor: 'var(--color-error-hover)',
  } as const,
};

// ============================================================================
// SPACING HELPERS
// ============================================================================

export const spacingStyles = {
  gap20: { gap: '20px' } as const,
  gap15: { gap: '15px' } as const,
  gap10: { gap: '10px' } as const,
  gap8: { gap: '8px' } as const,

  marginBottom20: { marginBottom: '20px' } as const,
  marginBottom15: { marginBottom: '15px' } as const,
  marginBottom10: { marginBottom: '10px' } as const,
  marginBottom5: { marginBottom: '5px' } as const,

  padding20: { padding: '20px' } as const,
  padding12: { padding: '12px' } as const,
};
