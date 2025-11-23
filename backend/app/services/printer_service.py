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

    def print_label(self, serial_number: str, model_code: str, production_date: str) -> bool:
        """
        Print a label for the given serial number.

        Args:
            serial_number: The serial number to print (e.g., KR01PSA2511001)
            model_code: Product model code (e.g., PSA)
            production_date: Production date string

        Returns:
            True if printing was successful, False otherwise.
        """
        zpl = self._generate_serial_zpl(serial_number, model_code, production_date)
        return self._send_to_printer(zpl, f"Serial: {serial_number}")

    def print_wip_label(self, wip_id: str) -> bool:
        """
        Print a WIP label (60mm x 30mm).

        Args:
            wip_id: WIP ID to print

        Returns:
            True if printing was successful, False otherwise.
        """
        zpl = self._generate_wip_zpl(wip_id)
        return self._send_to_printer(zpl, f"WIP: {wip_id}")

    def _send_to_printer(self, zpl: str, description: str) -> bool:
        """
        Send ZPL to network printer via TCP/IP.
        """
        try:
            logger.info(f"Sending print job to {self.printer_ip}:{self.printer_port} - {description}")
            
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.printer_ip, self.printer_port))
            
            # Send ZPL
            sock.send(zpl.encode('utf-8'))
            
            sock.close()
            logger.info(f"Print job sent successfully - {description}")
            return True
            
        except socket.timeout:
            logger.error(f"Printer connection timeout - {self.printer_ip}:{self.printer_port}")
            return False
        except socket.error as e:
            logger.error(f"Printer connection failed - {self.printer_ip}:{self.printer_port}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to print - {description}: {e}")
            return False

    def _generate_wip_zpl(self, wip_id: str) -> str:
        """
        Generate ZPL for WIP label (60mm x 30mm).
        203 DPI: 60mm = 472 dots, 30mm = 236 dots
        
        Layout (clean design):
        ┌────────────────────────────────────────┐
        │                                        │
        │                                        │
        │    F2X NEUROHUB - WIP LABEL            │
        │                                        │
        │    WIP ID:                 ████████    │
        │    WIP-KR01PSA2511-001     ████████    │
        │                            ████████    │
        │                            ████████    │
        └────────────────────────────────────────┘
        
        Print Quality Settings:
        - Speed: 1 (slowest, maximum quality)
        - Darkness: 29 (maximum darkness)
        - QR Code: Model 2, Magnification 5
        - Left Padding: 30 dots (~4mm)
        - Top Padding: 30 dots (~4mm)
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

    def _generate_serial_zpl(self, serial_number: str, model_code: str, production_date: str) -> str:
        """
        Generate ZPL code for serial label.
        
        Label Size: 40mm x 20mm (approx)
        Content:
        - Data Matrix Code (Serial Number)
        - Text: Serial Number
        - Text: Model Code
        """
        zpl = f"""^XA
^FO20,20^BXN,4,200^FD{serial_number}^FS
^FO100,30^ADN,36,20^FD{serial_number}^FS
^FO100,70^ADN,36,20^FDModel: {model_code}^FS
^FO100,110^ADN,36,20^FDDate: {production_date}^FS
^XZ"""
        return zpl.strip()

# Global instance
printer_service = PrinterService()
