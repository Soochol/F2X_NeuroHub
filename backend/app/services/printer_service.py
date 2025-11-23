import logging
import socket
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

class PrinterService:
    """
    Service for printing ZPL labels to Zebra printers.
    Supports both Windows print queue and direct network printing.
    """

    def __init__(self, queue_name: Optional[str] = None, printer_ip: str = "192.168.35.79", printer_port: int = 9100):
        self.queue_name = queue_name or getattr(settings, 'PRINTER_QUEUE_NAME', None)
        self.printer_ip = printer_ip
        self.printer_port = printer_port
        self.use_network_printer = True  # Use network printer by default

    def print_wip_label(self, wip_id: str) -> dict:
        """
        Print a WIP label (60mm x 30mm).

        Args:
            wip_id: WIP ID to print

        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            zpl = self._generate_wip_zpl(wip_id)
            self._send_to_printer(zpl)
            
            return {
                "success": True,
                "message": f"WIP label printed: {wip_id}"
            }
        except Exception as e:
            logger.error(f"Failed to print WIP label: {e}")
            return {
                "success": False,
                "message": f"Print failed: {str(e)}"
            }

    def print_serial_label(self, serial_number: str) -> dict:
        """
        Print Serial label.
        
        Args:
            serial_number: Serial number (e.g., 'WF-KR-251118D-001-0001')
            
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            zpl = self._generate_serial_zpl(serial_number)
            self._send_to_printer(zpl)
            
            return {
                "success": True,
                "message": f"Serial label printed: {serial_number}"
            }
        except Exception as e:
            logger.error(f"Failed to print serial label: {e}")
            return {
                "success": False,
                "message": f"Print failed: {str(e)}"
            }

    def print_lot_label(self, lot_number: str) -> dict:
        """
        Print LOT label.
        
        Args:
            lot_number: LOT number (e.g., 'DT01A10251101')
            
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            zpl = self._generate_lot_zpl(lot_number)
            self._send_to_printer(zpl)
            
            return {
                "success": True,
                "message": f"LOT label printed: {lot_number}"
            }
        except Exception as e:
            logger.error(f"Failed to print LOT label: {e}")
            return {
                "success": False,
                "message": f"Print failed: {str(e)}"
            }

    def _send_to_printer(self, zpl: str) -> bool:
        """
        Send ZPL to network printer via TCP/IP.
        """
        try:
            logger.info(f"Sending print job to {self.printer_ip}:{self.printer_port}")
            
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.printer_ip, self.printer_port))
            
            # Send ZPL
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
        """
        Generate ZPL for WIP label (60mm x 30mm).
        203 DPI: 60mm = 472 dots, 30mm = 236 dots
        """
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
        """
        Generate ZPL for Serial label (60mm x 30mm).
        203 DPI: 60mm = 472 dots, 30mm = 236 dots
        """
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
        """
        Generate ZPL for LOT label (60mm x 30mm).
        203 DPI: 60mm = 472 dots, 30mm = 236 dots
        """
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
