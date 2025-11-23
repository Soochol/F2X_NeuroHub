import logging
import socket
import time
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.models.print_log import PrintLog, PrintStatus

logger = logging.getLogger(__name__)

class PrinterService:
    """
    Service for printing ZPL labels to Zebra printers.
    Supports direct network printing with logging capabilities.
    """

    def __init__(self, queue_name: Optional[str] = None, printer_ip: str = "192.168.35.79", printer_port: int = 9100):
        self.queue_name = queue_name or getattr(settings, 'PRINTER_QUEUE_NAME', None)
        self.printer_ip = printer_ip
        self.printer_port = printer_port
        self.use_network_printer = True

    def check_printer_status(self) -> dict:
        """
        Check printer connection status.
        
        Returns:
            dict: {
                "online": bool,
                "ip": str,
                "port": int,
                "response_time_ms": float,
                "error": str (optional)
            }
        """
        start_time = time.time()
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((self.printer_ip, self.printer_port))
            sock.close()
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                "online": True,
                "ip": self.printer_ip,
                "port": self.printer_port,
                "response_time_ms": round(response_time, 2)
            }
        except socket.timeout:
            return {
                "online": False,
                "ip": self.printer_ip,
                "port": self.printer_port,
                "error": "Connection timeout"
            }
        except socket.error as e:
            return {
                "online": False,
                "ip": self.printer_ip,
                "port": self.printer_port,
                "error": f"Connection failed: {str(e)}"
            }
        except Exception as e:
            return {
                "online": False,
                "ip": self.printer_ip,
                "port": self.printer_port,
                "error": f"Unexpected error: {str(e)}"
            }

    def print_wip_label(
        self, 
        wip_id: str, 
        db: Optional[Session] = None,
        operator_id: Optional[int] = None,
        process_id: Optional[int] = None,
        process_data_id: Optional[int] = None
    ) -> dict:
        """
        Print a WIP label with logging.

        Args:
            wip_id: WIP ID to print
            db: Database session for logging
            operator_id: User who triggered the print
            process_id: Associated process ID
            process_data_id: Associated process data ID

        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            zpl = self._generate_wip_zpl(wip_id)
            self._send_to_printer(zpl)
            
            # Log success
            if db:
                self._log_print(
                    db=db,
                    label_type="WIP_LABEL",
                    label_id=wip_id,
                    status=PrintStatus.SUCCESS,
                    operator_id=operator_id,
                    process_id=process_id,
                    process_data_id=process_data_id
                )
            
            logger.info(f"WIP label printed successfully: {wip_id}")
            return {
                "success": True,
                "message": f"WIP label printed: {wip_id}"
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to print WIP label {wip_id}: {error_msg}")
            
            # Log failure
            if db:
                self._log_print(
                    db=db,
                    label_type="WIP_LABEL",
                    label_id=wip_id,
                    status=PrintStatus.FAILED,
                    error_message=error_msg,
                    operator_id=operator_id,
                    process_id=process_id,
                    process_data_id=process_data_id
                )
            
            return {
                "success": False,
                "message": f"Print failed: {error_msg}"
            }

    def print_serial_label(
        self, 
        serial_number: str,
        db: Optional[Session] = None,
        operator_id: Optional[int] = None,
        process_id: Optional[int] = None,
        process_data_id: Optional[int] = None
    ) -> dict:
        """
        Print Serial label with logging.
        
        Args:
            serial_number: Serial number
            db: Database session for logging
            operator_id: User who triggered the print
            process_id: Associated process ID
            process_data_id: Associated process data ID
            
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            zpl = self._generate_serial_zpl(serial_number)
            self._send_to_printer(zpl)
            
            # Log success
            if db:
                self._log_print(
                    db=db,
                    label_type="SERIAL_LABEL",
                    label_id=serial_number,
                    status=PrintStatus.SUCCESS,
                    operator_id=operator_id,
                    process_id=process_id,
                    process_data_id=process_data_id
                )
            
            logger.info(f"Serial label printed successfully: {serial_number}")
            return {
                "success": True,
                "message": f"Serial label printed: {serial_number}"
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to print Serial label {serial_number}: {error_msg}")
            
            # Log failure
            if db:
                self._log_print(
                    db=db,
                    label_type="SERIAL_LABEL",
                    label_id=serial_number,
                    status=PrintStatus.FAILED,
                    error_message=error_msg,
                    operator_id=operator_id,
                    process_id=process_id,
                    process_data_id=process_data_id
                )
            
            return {
                "success": False,
                "message": f"Print failed: {error_msg}"
            }

    def print_lot_label(
        self, 
        lot_number: str,
        db: Optional[Session] = None,
        operator_id: Optional[int] = None,
        process_id: Optional[int] = None,
        process_data_id: Optional[int] = None
    ) -> dict:
        """
        Print LOT label with logging.
        
        Args:
            lot_number: LOT number
            db: Database session for logging
            operator_id: User who triggered the print
            process_id: Associated process ID
            process_data_id: Associated process data ID
            
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            zpl = self._generate_lot_zpl(lot_number)
            self._send_to_printer(zpl)
            
            # Log success
            if db:
                self._log_print(
                    db=db,
                    label_type="LOT_LABEL",
                    label_id=lot_number,
                    status=PrintStatus.SUCCESS,
                    operator_id=operator_id,
                    process_id=process_id,
                    process_data_id=process_data_id
                )
            
            logger.info(f"LOT label printed successfully: {lot_number}")
            return {
                "success": True,
                "message": f"LOT label printed: {lot_number}"
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to print LOT label {lot_number}: {error_msg}")
            
            # Log failure
            if db:
                self._log_print(
                    db=db,
                    label_type="LOT_LABEL",
                    label_id=lot_number,
                    status=PrintStatus.FAILED,
                    error_message=error_msg,
                    operator_id=operator_id,
                    process_id=process_id,
                    process_data_id=process_data_id
                )
            
            return {
                "success": False,
                "message": f"Print failed: {error_msg}"
            }

    def _log_print(
        self,
        db: Session,
        label_type: str,
        label_id: str,
        status: PrintStatus,
        error_message: Optional[str] = None,
        operator_id: Optional[int] = None,
        process_id: Optional[int] = None,
        process_data_id: Optional[int] = None
    ):
        """
        Log print operation to database.
        """
        try:
            print_log = PrintLog(
                label_type=label_type,
                label_id=label_id,
                process_id=process_id,
                process_data_id=process_data_id,
                printer_ip=self.printer_ip,
                printer_port=self.printer_port,
                status=status.value,
                error_message=error_message,
                operator_id=operator_id,
                created_at=datetime.utcnow()
            )
            db.add(print_log)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log print operation: {e}")
            db.rollback()

    def _send_to_printer(self, zpl: str) -> bool:
        """
        Send ZPL to network printer via TCP/IP.
        """
        try:
            logger.info(f"Sending print job to {self.printer_ip}:{self.printer_port}")
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.printer_ip, self.printer_port))
            
            sock.send(zpl.encode('utf-8'))
            
            sock.close()
            logger.info(f"Print job sent successfully")
            return True
            
        except socket.timeout:
            logger.error(f"Printer connection timeout - {self.printer_ip}:{self.printer_port}")
            raise Exception("Printer connection timeout")
        except socket.error as e:
            logger.error(f"Printer connection failed - {self.printer_ip}:{self.printer_port}: {e}")
            raise Exception(f"Printer connection failed: {e}")
        except Exception as e:
            logger.error(f"Failed to print: {e}")
            raise

    def _generate_wip_zpl(self, wip_id: str) -> str:
        """Generate ZPL for WIP label (60mm x 30mm)."""
        zpl = f"""^XA
^MMT
^PW472
^LL236
^PR1,1
~SD29

^FO30,30^A0N,16,16^FDF2X NEUROHUB - WIP LABEL^FS

^FO30,65^A0N,14,14^FDWIP ID:^FS
^FO30,85^A0N,24,24^FD{wip_id}^FS

^FO340,65^BQN,2,5^FDQA,{wip_id}^FS

^PQ1
^XZ"""
        return zpl

    def _generate_serial_zpl(self, serial_number: str) -> str:
        """Generate ZPL for Serial label (60mm x 30mm)."""
        zpl = f"""^XA
^MMT
^PW472
^LL236
^PR1,1
~SD29

^FO30,30^A0N,16,16^FDF2X NEUROHUB - SERIAL LABEL^FS

^FO30,65^A0N,14,14^FDSerial No:^FS
^FO30,85^A0N,20,20^FD{serial_number}^FS

^FO340,65^BQN,2,5^FDQA,{serial_number}^FS

^PQ1
^XZ"""
        return zpl

    def _generate_lot_zpl(self, lot_number: str) -> str:
        """Generate ZPL for LOT label (60mm x 30mm)."""
        zpl = f"""^XA
^MMT
^PW472
^LL236
^PR1,1
~SD29

^FO30,30^A0N,16,16^FDF2X NEUROHUB - LOT LABEL^FS

^FO30,65^A0N,14,14^FDLOT No:^FS
^FO30,85^A0N,24,24^FD{lot_number}^FS

^FO340,65^BQN,2,5^FDQA,{lot_number}^FS

^PQ1
^XZ"""
        return zpl


# Singleton instance
printer_service = PrinterService()
