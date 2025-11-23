"""
Auto-print label helper functions for process operations.
"""
import logging
from sqlalchemy.orm import Session
from app.models import Process, ProcessData, WIPItem, Serial, Lot
from app.models.process import LabelTemplateType
from app.schemas.process_data import ProcessResult

logger = logging.getLogger(__name__)


def check_and_print_label(db: Session, process_data: ProcessData, wip_item=None, serial=None, lot=None) -> dict:
    """
    자동 라벨 프린팅 체크 및 실행
    
    Args:
        db: Database session
        process_data: Completed process data
        wip_item: WIP item (if applicable)
        serial: Serial (if applicable)
        lot: LOT (if applicable)
    
    Returns:
        {
            "printed": bool,
            "label_type": str,
            "error": str (optional)
        }
    """
    # 프로세스 정보 가져오기
    process = db.query(Process).filter(
        Process.id == process_data.process_id
    ).first()
    
    if not process:
        return {"printed": False}
    
    # 자동 프린팅 비활성화
    if not process.auto_print_label:
        return {"printed": False}
    
    # 라벨 종류 미설정
    if not process.label_template_type:
        logger.warning(f"Process {process.id} has auto_print enabled but no label_template_type")
        return {"printed": False}
    
    # PASS가 아니면 프린팅 안함
    if process_data.result != ProcessResult.PASS.value:
        return {"printed": False}
    
    # 이전 프로세스 검증
    if not validate_previous_processes(db, process, wip_item):
        logger.info(f"Previous processes not all PASS, skipping auto-print")
        return {"printed": False}
    
    # 라벨 프린팅 실행
    try:
        from app.services.printer_service import printer_service
        
        label_type = process.label_template_type
        operator_id = process_data.operator_id if process_data else None
        
        if label_type == LabelTemplateType.WIP_LABEL.value and wip_item:
            result = printer_service.print_wip_label(
                wip_id=wip_item.wip_id,
                db=db,
                operator_id=operator_id,
                process_id=process.id,
                process_data_id=process_data.id
            )
            if result.get("success"):
                logger.info(f"Auto-printed WIP label: {wip_item.wip_id}")
                return {
                    "printed": True,
                    "label_type": "WIP_LABEL"
                }
        
        elif label_type == LabelTemplateType.SERIAL_LABEL.value and serial:
            result = printer_service.print_serial_label(
                serial_number=serial.serial_number,
                db=db,
                operator_id=operator_id,
                process_id=process.id,
                process_data_id=process_data.id
            )
            if result.get("success"):
                logger.info(f"Auto-printed Serial label: {serial.serial_number}")
                return {
                    "printed": True,
                    "label_type": "SERIAL_LABEL"
                }
        
        elif label_type == LabelTemplateType.LOT_LABEL.value and lot:
            result = printer_service.print_lot_label(
                lot_number=lot.lot_number,
                db=db,
                operator_id=operator_id,
                process_id=process.id,
                process_data_id=process_data.id
            )
            if result.get("success"):
                logger.info(f"Auto-printed LOT label: {lot.lot_number}")
                return {
                    "printed": True,
                    "label_type": "LOT_LABEL"
                }
        
        return {"printed": False}
        
    except Exception as e:
        logger.error(f"Auto-print failed: {e}")
        return {
            "printed": False,
            "error": str(e)
        }


def validate_previous_processes(db: Session, process: Process, wip_item) -> bool:
    """
    이전 프로세스 모두 PASS 확인
    
    Args:
        db: Database session
        process: Current process
        wip_item: WIP item to check
        
    Returns:
        bool: True if all previous processes are PASS
    """
    if not wip_item:
        return False
    
    # 프로세스 1이면 이전 프로세스 없음
    if process.process_number == 1:
        return True
    
    # 이전 프로세스 1 ~ (current - 1) 모두 PASS 확인
    for prev_num in range(1, process.process_number):
        prev_process = db.query(Process).filter(
            Process.process_number == prev_num,
            Process.is_active == True
        ).first()
        
        if prev_process:
            prev_data = db.query(ProcessData).filter(
                ProcessData.wip_id == wip_item.id,
                ProcessData.process_id == prev_process.id,
                ProcessData.result == ProcessResult.PASS.value,
                ProcessData.completed_at.isnot(None)
            ).first()
            
            if not prev_data:
                logger.warning(
                    f"Previous process {prev_num} not PASS for WIP {wip_item.wip_id}"
                )
                return False
    
    return True
