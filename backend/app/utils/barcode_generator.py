"""
Barcode and QR code generation utilities.

This module provides functions for generating barcodes and QR codes for
WIP IDs, serial numbers, and LOT numbers in the F2X NeuroHub Manufacturing
Execution System.

Supports:
    - Code128 barcodes (1D linear barcodes)
    - QR codes (2D matrix barcodes)
    - ZPL (Zebra Programming Language) commands for Zebra label printers
    - PNG image output (BytesIO)

Dependencies:
    - python-barcode: For Code128 barcode generation
    - qrcode: For QR code generation
    - Pillow (PIL): For image processing

Functions:
    - generate_code128_barcode: Generate Code128 barcode as PNG image
    - generate_qr_code: Generate QR code as PNG image
    - generate_zpl_barcode: Generate ZPL command for Zebra printers
    - generate_barcode_image: Generic barcode generator (dispatches to specific type)
"""

import io
from io import BytesIO
from typing import Optional, Literal

try:
    import barcode
    from barcode.writer import ImageWriter
except ImportError:
    barcode = None
    ImageWriter = None

try:
    import qrcode
    from qrcode.image.pil import PilImage
except ImportError:
    qrcode = None
    PilImage = None


# Barcode generation constants
DEFAULT_BARCODE_FORMAT = "code128"
DEFAULT_QR_VERSION = 1
DEFAULT_QR_BOX_SIZE = 10
DEFAULT_QR_BORDER = 4
DEFAULT_IMAGE_FORMAT = "PNG"


def generate_code128_barcode(
    data: str,
    writer_options: Optional[dict] = None,
) -> BytesIO:
    """
    Generate Code128 barcode as PNG image in memory.

    Code128 is a high-density linear barcode symbology that can encode
    the full ASCII character set. It's commonly used for product identification,
    inventory control, and shipping labels.

    Args:
        data: Data to encode (WIP ID, serial number, or LOT number)
        writer_options: Optional writer configuration (module_width, module_height, etc.)

    Returns:
        BytesIO containing PNG image data

    Raises:
        ImportError: If python-barcode is not installed
        ValueError: If data is invalid

    Examples:
        >>> barcode_image = generate_code128_barcode("WIP-KR01PSA2511-001")
        >>> with open("barcode.png", "wb") as f:
        ...     f.write(barcode_image.getvalue())

        >>> barcode_image = generate_code128_barcode(
        ...     "WIP-KR01PSA2511-001",
        ...     writer_options={"module_width": 0.3, "module_height": 10.0}
        ... )
    """
    if barcode is None or ImageWriter is None:
        raise ImportError(
            "python-barcode is required for barcode generation. "
            "Install it with: pip install python-barcode[images]"
        )

    if not data:
        raise ValueError("data is required for barcode generation")

    # Default writer options
    default_options = {
        "module_width": 0.2,  # Width of narrowest bar in mm
        "module_height": 15.0,  # Height of bars in mm
        "quiet_zone": 6.5,  # Quiet zone in mm
        "font_size": 10,  # Font size for human-readable text
        "text_distance": 5.0,  # Distance between bars and text
        "write_text": True,  # Include human-readable text
    }

    # Merge custom options with defaults
    if writer_options:
        default_options.update(writer_options)

    # Generate Code128 barcode
    code128_class = barcode.get_barcode_class("code128")
    barcode_instance = code128_class(data, writer=ImageWriter())

    # Write to BytesIO
    output = BytesIO()
    barcode_instance.write(output, options=default_options)
    output.seek(0)

    return output


def generate_qr_code(
    data: str,
    version: int = DEFAULT_QR_VERSION,
    box_size: int = DEFAULT_QR_BOX_SIZE,
    border: int = DEFAULT_QR_BORDER,
    error_correction: Literal["L", "M", "Q", "H"] = "M",
) -> BytesIO:
    """
    Generate QR code as PNG image in memory.

    QR codes can store more data than linear barcodes and can be scanned
    from any angle. They're ideal for mobile scanning applications.

    Args:
        data: Data to encode (WIP ID, serial number, LOT number, or JSON data)
        version: QR code version (1-40, None for auto, default: 1)
        box_size: Size of each box in pixels (default: 10)
        border: Border size in boxes (default: 4, minimum per spec)
        error_correction: Error correction level (L, M, Q, H, default: M)
            - L: ~7% error correction
            - M: ~15% error correction (default, good balance)
            - Q: ~25% error correction
            - H: ~30% error correction

    Returns:
        BytesIO containing PNG image data

    Raises:
        ImportError: If qrcode is not installed
        ValueError: If data is invalid

    Examples:
        >>> qr_image = generate_qr_code("WIP-KR01PSA2511-001")
        >>> with open("qrcode.png", "wb") as f:
        ...     f.write(qr_image.getvalue())

        >>> qr_image = generate_qr_code(
        ...     "WIP-KR01PSA2511-001",
        ...     box_size=20,
        ...     error_correction="H"
        ... )
    """
    if qrcode is None:
        raise ImportError(
            "qrcode is required for QR code generation. "
            "Install it with: pip install qrcode[pil]"
        )

    if not data:
        raise ValueError("data is required for QR code generation")

    # Error correction level mapping
    error_correction_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }

    if error_correction not in error_correction_map:
        raise ValueError(
            f"Invalid error_correction: {error_correction}. "
            f"Valid values: L, M, Q, H"
        )

    # Create QR code instance
    qr = qrcode.QRCode(
        version=version,
        error_correction=error_correction_map[error_correction],
        box_size=box_size,
        border=border,
    )

    # Add data and generate
    qr.add_data(data)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Write to BytesIO
    output = BytesIO()
    img.save(output, format=DEFAULT_IMAGE_FORMAT)
    output.seek(0)

    return output


def generate_zpl_barcode(
    data: str,
    barcode_type: Literal["code128", "qr"] = "code128",
    width: int = 2,
    height: int = 100,
    x_position: int = 50,
    y_position: int = 50,
    include_text: bool = True,
) -> str:
    """
    Generate ZPL (Zebra Programming Language) command for Zebra label printers.

    ZPL is a printer control language used by Zebra Technologies label printers.
    This function generates ZPL commands to print barcodes directly on Zebra printers
    without needing to generate image files.

    Args:
        data: Data to encode (WIP ID, serial number, LOT number)
        barcode_type: Barcode type ("code128" or "qr", default: "code128")
        width: Bar width multiplier (1-10, default: 2)
        height: Barcode height in dots (default: 100)
        x_position: X position in dots (default: 50)
        y_position: Y position in dots (default: 50)
        include_text: Include human-readable text below barcode (default: True)

    Returns:
        ZPL command string ready to send to Zebra printer

    Raises:
        ValueError: If parameters are invalid

    Examples:
        >>> zpl = generate_zpl_barcode("WIP-KR01PSA2511-001")
        >>> print(zpl)
        ^XA
        ^FO50,50
        ^BY2,3,100
        ^BCN,100,Y,N,N
        ^FDWIP-KR01PSA2511-001^FS
        ^XZ

        >>> zpl = generate_zpl_barcode(
        ...     "WIP-KR01PSA2511-001",
        ...     barcode_type="qr",
        ...     width=5
        ... )
    """
    if not data:
        raise ValueError("data is required for ZPL barcode generation")

    if barcode_type not in ("code128", "qr"):
        raise ValueError("barcode_type must be 'code128' or 'qr'")

    if width < 1 or width > 10:
        raise ValueError("width must be between 1 and 10")

    # Start ZPL label
    zpl_commands = ["^XA"]  # Start format

    # Set field origin (position)
    zpl_commands.append(f"^FO{x_position},{y_position}")

    if barcode_type == "code128":
        # Code128 barcode
        # ^BY: Bar code field default
        #   width (1-10), wide-to-narrow ratio (2.0-3.0), height
        zpl_commands.append(f"^BY{width},3,{height}")

        # ^BC: Code128 barcode
        #   N = normal orientation
        #   height = barcode height
        #   Y/N = print interpretation line (human-readable text)
        #   N = no line above
        #   N = no UCC check digit
        interpretation = "Y" if include_text else "N"
        zpl_commands.append(f"^BCN,{height},{interpretation},N,N")

        # ^FD: Field data
        zpl_commands.append(f"^FD{data}^FS")

    elif barcode_type == "qr":
        # QR code
        # ^BQ: QR code
        #   N = normal orientation
        #   2 = model 2 (standard QR code)
        #   width = magnification factor (1-10)
        zpl_commands.append(f"^BQN,2,{width}")

        # ^FD: Field data with encoding
        #   QA = Quality (A = automatic error correction)
        zpl_commands.append(f"^FDQA,{data}^FS")

        # Add text below QR code if requested
        if include_text:
            text_y = y_position + (width * 30) + 10  # Position below QR code
            zpl_commands.append(f"^FO{x_position},{text_y}")
            zpl_commands.append("^A0N,20,20")  # Font: 0, Normal, 20x20
            zpl_commands.append(f"^FD{data}^FS")

    # End ZPL label
    zpl_commands.append("^XZ")  # End format

    return "\n".join(zpl_commands)


def generate_barcode_image(
    data: str,
    barcode_type: Literal["code128", "qr"] = "code128",
    **kwargs,
) -> BytesIO:
    """
    Generic barcode generator that dispatches to specific barcode type.

    Convenience function to generate barcodes without needing to know
    which specific function to call.

    Args:
        data: Data to encode
        barcode_type: Type of barcode ("code128" or "qr", default: "code128")
        **kwargs: Additional arguments passed to specific generator

    Returns:
        BytesIO containing PNG image data

    Raises:
        ValueError: If barcode_type is invalid
        ImportError: If required libraries are not installed

    Examples:
        >>> barcode_img = generate_barcode_image("WIP-KR01PSA2511-001")
        >>> qr_img = generate_barcode_image("WIP-KR01PSA2511-001", barcode_type="qr")
    """
    if barcode_type == "code128":
        writer_options = kwargs.get("writer_options")
        return generate_code128_barcode(data, writer_options=writer_options)

    elif barcode_type == "qr":
        version = kwargs.get("version", DEFAULT_QR_VERSION)
        box_size = kwargs.get("box_size", DEFAULT_QR_BOX_SIZE)
        border = kwargs.get("border", DEFAULT_QR_BORDER)
        error_correction = kwargs.get("error_correction", "M")
        return generate_qr_code(
            data,
            version=version,
            box_size=box_size,
            border=border,
            error_correction=error_correction,
        )

    else:
        raise ValueError(
            f"Invalid barcode_type: {barcode_type}. "
            f"Valid values: code128, qr"
        )
