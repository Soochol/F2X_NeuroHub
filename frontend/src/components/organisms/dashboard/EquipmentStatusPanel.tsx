/**
 * Equipment Status Panel Component
 * Displays equipment status grid for dashboard monitoring
 */

import { useEffect, useState, useMemo } from 'react';
import { Tooltip, Spin, Typography } from 'antd';
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  Wrench,
  Clock,
  Zap
} from 'lucide-react';
import { equipmentApi } from '@/api';
import type { Equipment } from '@/types/api';
import Logger from '@/utils/logger';
import styles from './EquipmentStatusPanel.module.css';

interface EquipmentStatusPanelProps {
  productionLineId?: number;
  showMaintenanceWarnings?: boolean;
  refreshInterval?: number; // in milliseconds
  className?: string;
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'AVAILABLE':
      return <CheckCircle size={18} className={styles.iconAvailable} />;
    case 'IN_USE':
      return <Zap size={18} className={styles.iconInUse} />;
    case 'MAINTENANCE':
      return <Wrench size={18} className={styles.iconMaintenance} />;
    case 'OUT_OF_SERVICE':
      return <XCircle size={18} className={styles.iconOutOfService} />;
    default:
      return <Clock size={18} className={styles.iconDefault} />;
  }
};

const getStatusLabel = (status: string): string => {
  switch (status) {
    case 'AVAILABLE':
      return 'Available';
    case 'IN_USE':
      return 'In Use';
    case 'MAINTENANCE':
      return 'Maintenance';
    case 'OUT_OF_SERVICE':
      return 'Out of Service';
    case 'RETIRED':
      return 'Retired';
    default:
      return status;
  }
};

const getStatusClass = (status: string): string => {
  switch (status) {
    case 'AVAILABLE':
      return styles.statusAvailable;
    case 'IN_USE':
      return styles.statusInUse;
    case 'MAINTENANCE':
      return styles.statusMaintenance;
    case 'OUT_OF_SERVICE':
      return styles.statusOutOfService;
    default:
      return '';
  }
};

const isMaintenanceDueSoon = (equipment: Equipment): boolean => {
  if (!equipment.next_maintenance_date) return false;

  const nextDate = new Date(equipment.next_maintenance_date);
  const today = new Date();
  const daysUntil = Math.ceil((nextDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

  return daysUntil <= 7 && daysUntil >= 0;
};

const formatDate = (dateStr?: string): string => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleDateString('ko-KR', {
    month: 'short',
    day: 'numeric',
  });
};

export const EquipmentStatusPanel = ({
  productionLineId,
  showMaintenanceWarnings = true,
  refreshInterval = 30000,
  className,
}: EquipmentStatusPanelProps) => {
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEquipment = async () => {
    try {
      let data: Equipment[];
      if (productionLineId) {
        data = await equipmentApi.getEquipmentByLine(productionLineId);
      } else {
        data = await equipmentApi.getActiveEquipment();
      }
      setEquipment(data);
      setError(null);
    } catch (err) {
      Logger.error('Failed to fetch equipment:', err);
      setError('Failed to load equipment status');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEquipment();

    const interval = setInterval(fetchEquipment, refreshInterval);
    return () => clearInterval(interval);
  }, [productionLineId, refreshInterval]);

  // Summary stats
  const stats = useMemo(() => {
    const total = equipment.length;
    const available = equipment.filter(e => e.status === 'AVAILABLE').length;
    const inUse = equipment.filter(e => e.status === 'IN_USE').length;
    const maintenance = equipment.filter(e => e.status === 'MAINTENANCE').length;
    const outOfService = equipment.filter(e => e.status === 'OUT_OF_SERVICE').length;
    const needsMaintenance = equipment.filter(e => isMaintenanceDueSoon(e)).length;

    return {
      total,
      available,
      inUse,
      maintenance,
      outOfService,
      needsMaintenance,
      online: available + inUse,
    };
  }, [equipment]);

  if (isLoading) {
    return (
      <div className={`${styles.container} ${className || ''}`}>
        <div className={styles.loading}>
          <Spin size="small" />
          <span>Loading equipment...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${styles.container} ${className || ''}`}>
        <div className={styles.error}>{error}</div>
      </div>
    );
  }

  return (
    <div className={`${styles.container} ${className || ''}`}>
      <div className={styles.header}>
        <Typography.Title level={4} style={{ margin: 0 }}>Equipment Status</Typography.Title>
        <span className={styles.summary}>
          {stats.online}/{stats.total} Online
        </span>
      </div>

      {/* Vertical List */}
      <div className={styles.list}>
        {equipment.map((item) => (
          <Tooltip
            key={item.id}
            placement="left"
            title={
              <div className={styles.tooltip}>
                <div><strong>{item.equipment_name}</strong></div>
                <div>Type: {item.equipment_type}</div>
                <div>Status: {getStatusLabel(item.status)}</div>
                {item.last_maintenance_date && (
                  <div>Last Maintenance: {formatDate(item.last_maintenance_date)}</div>
                )}
                {item.next_maintenance_date && (
                  <div>Next Maintenance: {formatDate(item.next_maintenance_date)}</div>
                )}
                {item.total_operation_hours !== undefined && (
                  <div>Operation Hours: {item.total_operation_hours.toLocaleString()}h</div>
                )}
              </div>
            }
          >
            <div className={`${styles.listItem} ${getStatusClass(item.status)}`}>
              {/* Status Icon */}
              <div className={styles.listIcon}>
                {getStatusIcon(item.status)}
              </div>

              {/* Equipment Info */}
              <div className={styles.listInfo}>
                <span className={styles.listName}>{item.equipment_code}</span>
                <span className={styles.listType}>{item.equipment_type}</span>
              </div>

              {/* Status Badge */}
              <div className={styles.listStatus}>
                <span className={`${styles.statusBadge} ${getStatusClass(item.status)}`}>
                  {getStatusLabel(item.status)}
                </span>
                {showMaintenanceWarnings && isMaintenanceDueSoon(item) && (
                  <AlertTriangle size={14} className={styles.maintenanceWarning} />
                )}
              </div>
            </div>
          </Tooltip>
        ))}
      </div>

      {/* Legend */}
      <div className={styles.legend}>
        <div className={styles.legendItem}>
          <span className={`${styles.legendDot} ${styles.dotAvailable}`} />
          <span>Available</span>
        </div>
        <div className={styles.legendItem}>
          <span className={`${styles.legendDot} ${styles.dotInUse}`} />
          <span>In Use</span>
        </div>
        <div className={styles.legendItem}>
          <span className={`${styles.legendDot} ${styles.dotMaintenance}`} />
          <span>Maintenance</span>
        </div>
        <div className={styles.legendItem}>
          <span className={`${styles.legendDot} ${styles.dotOutOfService}`} />
          <span>Out of Service</span>
        </div>
      </div>
    </div>
  );
};
