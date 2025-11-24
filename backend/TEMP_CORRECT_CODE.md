# Temp file - complete start_process method

Complete `start_process` method with all required code:

```python
def start_process(self, db: Session, request: ProcessStartRequest) -> ProcessStartResponse:
    """Register process start (착공 등록)."""
    try:
        # Find LOT by number
        lot_number = request.lot_number
        lot = db.query(Lot).filter(Lot.lot_number == lot_number).first()

        # Track if we found WIP item in Smart Lookup
        wip_from_smart_lookup = None
        wip_id_from_smart_lookup = None

        # If LOT not found, try to interpret as Serial, WIP ID, or Unit Barcode
        if not lot:
            # 1. Try as Serial Number
            serial = db.query(Serial).filter(Serial.serial_number == lot_number).first()
            if serial:
                lot = serial.lot
                if not request.serial_number:
                    request.serial_number = serial.serial_number

            # 2. Try as WIP ID
            elif lot_number.startswith("WIP-"):
                wip = db.query(WIPItem).filter(WIPItem.wip_id == lot_number).first()
                if wip:
                    lot = wip.lot
                    if not request.wip_id:
                        request.wip_id = wip.wip_id
                    wip_from_smart_lookup = wip
                    wip_id_from_smart_lookup = wip.id

            # 3. Try as Unit Barcode
            elif len(lot_number) > 13 and lot_number[-3:].isdigit():
                potential_lot_num = lot_number[:-3]
                potential_seq = lot_number[-3:]

                lot = db.query(Lot).filter(Lot.lot_number == potential_lot_num).first()
                if lot:
                    wip_id_str = f"WIP-{potential_lot_num}-{potential_seq}"
                    wip = db.query(WIPItem).filter(WIPItem.wip_id == wip_id_str).first()
                    if wip:
                        if not request.wip_id:
                            request.wip_id = wip.wip_id

        if not lot:
            raise LotNotFoundException(lot_number=request.lot_number)

        # Check LOT status
        self.check_business_rule(
            lot.status in [LotStatus.CREATED, LotStatus.IN_PROGRESS],
            f"LOT is not active. Current status: {lot.status}"
        )

        # Find Process
        process = self._resolve_process(db, request.process_id)
        if not process:
            raise ProcessNotFoundException(process_id=request.process_id)

        # Determine data level, serial, and WIP
        serial = None
        wip_item = wip_from_smart_lookup
        data_level = DataLevel.LOT
        serial_id = None
        wip_item_id = wip_id_from_smart_lookup

        if request.serial_number:
            serial = db.query(Serial).filter(
                Serial.serial_number == request.serial_number,
                Serial.lot_id == lot.id
            ).first()
            if not serial:
                raise SerialNotFoundException(serial_id=request.serial_number)
            data_level = DataLevel.SERIAL
            serial_id = serial.id
        elif request.wip_id:
            if not wip_item:
                wip_item = db.query(WIPItem).filter(
                    WIPItem.wip_id == request.wip_id,
                    WIPItem.lot_id == lot.id
                ).first()
                if not wip_item:
                    raise ValidationException(
                        message=f"WIP item '{request.wip_id}' not found for LOT {lot.lot_number}"
                    )
                wip_item_id = wip_item.id
            data_level = DataLevel.WIP

        # Validate Data Level for Manufacturing Processes
        if process.process_number in [1, 2, 3, 4, 5, 6] and data_level == DataLevel.LOT:
            raise BusinessRuleException(
                message=f"Process {process.process_number} requires a specific WIP ID or Serial Number. LOT level start is not allowed."
            )

        # Find operator
        operator = self._resolve_operator(db, request.worker_id)
        if not operator:
            raise UserNotFoundException(user_id=request.worker_id)

        # Find equipment
        equipment_id = None
        if request.equipment_id:
            equipment = db.query(Equipment).filter(
                Equipment.equipment_code == request.equipment_id
            ).first()
            if equipment:
                equipment_id = equipment.id

        # Update LOT production line if needed
        if request.line_id:
            production_line = db.query(ProductionLine).filter(
                ProductionLine.line_code == request.line_id
            ).first()
            if production_line and not lot.production_line_id:
                lot.production_line_id = production_line.id

        # Validate process sequence
        self._validate_process_sequence(db, lot, process, serial_id, wip_item_id)

        # Check for concurrent work
        self._check_concurrent_work(db, lot, process, serial_id, wip_item_id)

        # Create process data record
        if request.start_time:
            try:
                started_at = datetime.fromisoformat(request.start_time.replace('Z', '+00:00'))
            except ValueError:
                started_at = datetime.utcnow()
        else:
            started_at = datetime.utcnow()

        process_data_create = ProcessDataCreate(
            lot_id=lot.id,
            serial_id=serial_id,
            wip_id=wip_item_id,
            process_id=process.id,
            operator_id=operator.id,
            equipment_id=equipment_id,
            data_level=data_level,
            result=ProcessResult.PASS,
            measurements={},
            started_at=started_at,
            completed_at=None,
        )

        with self.transaction(db):
            process_data = crud.process_data.create(db, obj_in=process_data_create)

            if lot.status == LotStatus.CREATED:
                lot.status = LotStatus.IN_PROGRESS

            # Update WIP status if needed
            if wip_item and wip_item.status == WIPStatus.CREATED.value:
                wip_item.status = WIPStatus.IN_PROGRESS.value

            db.refresh(process_data)

            self.log_operation("start_process", process_data.id, {
                "lot_id": lot.id,
                "process_id": process.id
            })

            return ProcessStartResponse(
                success=True,
                message=f"Process {process.process_number} started successfully",
                process_data_id=process_data.id,
                started_at=process_data.started_at
            )

    except (LotNotFoundException, ProcessNotFoundException, SerialNotFoundException,
            UserNotFoundException, ValidationException, BusinessRuleException) as e:
        # Re-raise business exceptions as-is
        raise
    except IntegrityError as e:
        self.handle_integrity_error(
            e,
            resource_type="ProcessData",
            identifier=f"lot_id={lot.id if lot else 'unknown'}, process_id={process.id if process else 'unknown'}",
            operation="start"
        )
    except SQLAlchemyError as e:
        self.handle_sqlalchemy_error(e, operation="start_process")
```

This is the COMPLETE and CORRECT `start_process` method. The key fixes:
1. Added `success=True` field
2. Added `started_at=process_data.started_at` field 
3. Completed the `with self.transaction(db):` block with all missing code
