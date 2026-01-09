import logging
from pymodbus.client import AsyncModbusTcpClient
from .modbus_map import SENSOR_DEFINITIONS

_LOGGER = logging.getLogger(__name__)


def group_register_blocks(sensor_defs, max_gap=2):
    sorted_addresses = sorted(sensor_defs.keys())
    blocks = []
    block = []
    last_end = None

    for addr in sorted_addresses:
        t = sensor_defs[addr]["type"]
        if t in ("uint16", "int16"):
            reg_size = 1
        elif t in ("uint32", "int32"):
            reg_size = 2
        else:
            reg_size = 4

        if last_end is None or addr <= last_end + max_gap:
            block.append((addr, reg_size))
            last_end = addr + reg_size - 1
        else:
            blocks.append(block)
            block = [(addr, reg_size)]
            last_end = addr + reg_size - 1
    if block:
        blocks.append(block)

    _LOGGER.debug("Gruppierte Modbus-Registerblöcke: %s", blocks)
    return blocks


class KsemModbusClient:
    def __init__(self, host: str, port: int = 502, unit_id: int = 1):
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self._client = None

    async def connect(self):
        if not self._client:
            # old: self._client = AsyncModbusTcpClient(self.host, port=self.port)
            # Client erzeugen (versionssicher)
            try:
                # Neuere pymodbus-Versionen akzeptieren unit_id direkt
                self._client = AsyncModbusTcpClient(
                    self.host, port=self.port, timeout=5, unit_id=self.unit_id
                )
            except TypeError:
                # Ältere/andere Builds: ohne unit_id instanzieren und danach setzen
                self._client = AsyncModbusTcpClient(
                    self.host, port=self.port, timeout=5
                )
                try:
                    setattr(self._client, "unit_id", self.unit_id)
                except Exception:
                    pass
            await self._client.connect()
            _LOGGER.debug(
                "Modbus TCP verbunden mit %s:%s (Unit %s)",
                self.host,
                self.port,
                self.unit_id,
            )

    async def disconnect(self):
        if self._client:
            await self._client.close()
            self._client = None
            self._protocol = None
            _LOGGER.debug("Modbus TCP Verbindung getrennt")

    async def read_all(self):
        if not self._client:
            await self.connect()

        def _decode_fallback(raw_regs, dtype: str, word_order: str = "big"):
            """Einfacher Decoder für häufige Typen, falls convert_from_registers nicht vorhanden ist."""
            # Modbus-Word-Order: "big" = high word zuerst (KSEM nutzt Big Endian laut Doku)
            words = list(raw_regs)
            if word_order.lower() != "big":
                words = list(reversed(words))

            def _u16(w0):
                return w0 & 0xFFFF

            def _s16(w0):
                v = w0 & 0xFFFF
                return v - 0x10000 if v & 0x8000 else v

            def _u32(w0, w1):
                return ((w0 & 0xFFFF) << 16) | (w1 & 0xFFFF)

            def _s32(w0, w1):
                u = _u32(w0, w1)
                return u - 0x1_0000_0000 if u & 0x8000_0000 else u

            def _u64(w0, w1, w2, w3):
                return (
                    ((w0 & 0xFFFF) << 48)
                    | ((w1 & 0xFFFF) << 32)
                    | ((w2 & 0xFFFF) << 16)
                    | (w3 & 0xFFFF)
                )

            dtype = dtype.upper()
            n = len(words)

            if dtype in ("UINT16", "U16") and n >= 1:
                return _u16(words[0])
            if dtype in ("INT16", "S16") and n >= 1:
                return _s16(words[0])

            if dtype in ("UINT32", "U32") and n >= 2:
                return _u32(words[0], words[1])
            if dtype in ("INT32", "S32") and n >= 2:
                return _s32(words[0], words[1])

            if dtype in ("UINT64", "U64") and n >= 4:
                return _u64(words[0], words[1], words[2], words[3])

            # Float/andere Typen kannst du bei Bedarf ergänzen.
            raise ValueError(
                f"Fallback-Decoder: Unsupported dtype '{dtype}' with {n} regs"
            )

        data = {}
        blocks = group_register_blocks(SENSOR_DEFINITIONS, max_gap=0)

        for block in blocks:
            start = block[0][0]
            total_words = sum(size for _, size in block)

            try:
                # ---------- PyModbus 2/3/4-kompatibler Read ----------
                try:
                    result = await self._client.read_holding_registers(
                        address=start, count=total_words, unit=self.unit_id
                    )
                except TypeError:
                    try:
                        result = await self._client.read_holding_registers(
                            address=start, count=total_words, slave=self.unit_id
                        )
                    except TypeError:
                        try:
                            result = await self._client.read_holding_registers(
                                address=start, count=total_words
                            )  # nutzt evtl. client.unit_id
                        except TypeError:
                            try:
                                result = await self._client.read_holding_registers(
                                    start, total_words
                                )  # positionsbasiert
                            except TypeError:
                                result = await self._client.read_holding_registers(
                                    start
                                )  # letzter Fallback

                # ---------- Ergebnis prüfen ----------
                if result is None or getattr(result, "isError", lambda: False)():
                    _LOGGER.warning(
                        "Modbus-Fehler beim Lesen von %s-%s: %s",
                        start,
                        start + total_words,
                        result,
                    )
                    continue

                registers = getattr(result, "registers", None)
                if not registers or len(registers) < total_words:
                    _LOGGER.warning(
                        "Zu wenig Register erhalten (%s/%s) für Block %s-%s",
                        0 if not registers else len(registers),
                        total_words,
                        start,
                        start + total_words,
                    )
                    continue

                # ---------- Entpacken / Konvertieren ----------
                offset = 0
                for addr, size in block:
                    spec = SENSOR_DEFINITIONS[addr]
                    raw_regs = registers[offset : offset + size]

                    try:
                        # Versuch 1: dein bisheriger Weg über DATATYPE/convert_from_registers
                        datatype_name = spec["type"].upper()
                        datatype_enum = getattr(
                            getattr(self._client, "DATATYPE", None), datatype_name, None
                        )
                        if datatype_enum is not None and hasattr(
                            self._client, "convert_from_registers"
                        ):
                            val = self._client.convert_from_registers(
                                raw_regs,
                                data_type=datatype_enum,
                                # byteorder="big",  # bei Bedarf aktivieren
                                word_order="big",
                            )
                        else:
                            # Versuch 2: Fallback-Decoder (unterstützt die gängigen Integer-Typen)
                            val = _decode_fallback(
                                raw_regs, datatype_name, word_order="big"
                            )

                    except Exception as err:
                        _LOGGER.warning(
                            "Fehler beim Konvertieren von %s (Addr %s / %s Regs): %s",
                            spec.get("name", addr),
                            addr,
                            size,
                            err,
                        )
                        offset += size
                        continue

                    scaled_val = val * spec.get("scale", 1)
                    _LOGGER.debug(
                        "%s (%s): %s → skaliert: %s %s",
                        spec.get("name", addr),
                        addr,
                        val,
                        scaled_val,
                        spec.get("unit", ""),
                    )
                    data[spec["name"]] = scaled_val
                    offset += size

            except Exception as e:
                _LOGGER.exception(
                    "Fehler beim Modbus-Blocklesen (Start=0x%04X, Words=%s): %s",
                    start,
                    total_words,
                    e,
                )

        _LOGGER.debug("Alle OBIS-Daten gelesen: %s", data)
        return data
