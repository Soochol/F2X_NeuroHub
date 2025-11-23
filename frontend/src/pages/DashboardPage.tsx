import { useEffect, useState } from 'react';
import { dashboardApi } from '@/api';
import type { DashboardSummary } from '@/types/api';
import { getErrorMessage } from '@/types/api';
import { ProcessFlowDiagram } from '@/components/charts';
import { LotHistoryTabs } from '@/components/organisms/dashboard/LotHistoryTabs';
import styles from './DashboardPage.module.css';

export const DashboardPage = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const data = await dashboardApi.getSummary();
        setSummary(data);
      } catch (err: unknown) {
        setError(getErrorMessage(err, 'Failed to load dashboard data'));
      } finally {
        setIsLoading(false);
      }
    };

    fetchSummary();

    const interval = setInterval(fetchSummary, 10000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        Loading dashboard...
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorContainer}>
        Error: {error}
      </div>
    );
  }

  if (!summary) {
    return (
      <div className={styles.emptyContainer}>
        No data available
      </div>
    );
  }

  // Calculate metrics
  const completionRate = summary.total_started > 0
    ? (summary.total_completed / summary.total_started) * 100
    : 0;

  return (
    <div>
      <h1 className={styles.pageTitle}>
        Production Dashboard
      </h1>

      {/* KPI Cards */}
      <div className={styles.gridContainer}>
        {/* Started */}
        <div className={`${styles.card} ${styles.cardCenter}`}>
          <div className={styles.cardTitle}>
            Started
          </div>
          <div className={`${styles.cardValue} ${styles.textInfo}`}>
            {summary.total_started}
          </div>
          <div className={styles.cardSubtext}>
            units in production
          </div>
        </div>

        {/* In Progress */}
        <div className={`${styles.card} ${styles.cardCenter}`}>
          <div className={styles.cardTitle}>
            In Progress
          </div>
          <div className={`${styles.cardValue} ${styles.textWarning}`}>
            {summary.total_in_progress}
          </div>
          <div className={styles.cardSubtext}>
            units being processed
          </div>
        </div>

        {/* Completed */}
        <div className={`${styles.card} ${styles.cardCenter}`}>
          <div className={styles.cardTitle}>
            Completed
          </div>
          <div className={`${styles.cardValue} ${styles.textSuccess}`}>
            {summary.total_completed}
          </div>
          <div className={styles.cardSubtext}>
            units finished
          </div>
        </div>

        {/* Completion Rate */}
        <div className={`${styles.card} ${styles.cardCenter}`}>
          <div className={styles.cardTitle}>
            Completion Rate
          </div>
          <div className={`${styles.cardValueSmall} ${styles.textBrand}`}>
            {summary.total_completed} / {summary.total_started}
          </div>
          <div className={`${styles.cardValueMedium} ${styles.textBrand}`}>
            ({completionRate.toFixed(1)}%)
          </div>
        </div>

        {/* Defect Rate */}
        <div className={`${styles.card} ${styles.cardCenter}`}>
          <div className={styles.cardTitle}>
            Defect Rate
          </div>
          <div className={`${styles.cardValueSmall} ${summary.defect_rate > 5 ? styles.textError : styles.textWarning}`}>
            {summary.total_defective} / {summary.total_completed}
          </div>
          <div className={`${styles.cardValueMedium} ${summary.defect_rate > 5 ? styles.textError : styles.textWarning}`}>
            ({summary.defect_rate.toFixed(1)}%)
          </div>
        </div>
      </div>

      {/* Process Flow Diagram */}
      <div className={styles.sectionContainer}>
        <h2 className={styles.sectionTitle}>
          Process Flow Status
        </h2>
        <ProcessFlowDiagram data={summary.process_wip} />
      </div>

      {/* LOT History Tabs */}
      <div className={styles.card}>
        <h2 className={`${styles.sectionTitle} ${styles.sectionTitleLarge}`}>
          LOT History
        </h2>
        <LotHistoryTabs lots={summary.lots} />
      </div>
    </div>
  );
};

