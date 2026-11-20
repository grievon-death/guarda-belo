from datetime import datetime
from enum import Enum
from typing import List, NamedTuple
from struct import Struct


class LastCommandType(Enum):
    LAST = 1
    WTMPDB = 2
    UNKNOW = 99


class UTMPTypeMap(Enum):
    EMPTY = 0
    RUN_LVL = 1
    BOOT_TIME = 2
    NEW_TIME = 3
    OLD_TIME = 4
    INIT_PROCESS = 5
    LOGIN_PROCESS = 6
    USER_PROCESS = 7
    DEAD_PROCESS = 8
    ACCOUNTING = 9


class UTMPRawData(NamedTuple):
    registry_type: UTMPTypeMap
    pid: int
    user_terminal: bytes
    inittab_id: bytes
    user_name: bytes
    remote_host: bytes
    process_finish_code: int
    process_exit_code: int
    session_id: int
    timestamp: int
    timestamp_microsec: int
    remote_addr: tuple[int, int, int, int]
    reserved: bytes

    @classmethod
    def from_bytes(cls, chunk: bytes, utmp: Struct) -> 'UTMPRawData':
        (registry_type, pid, user_terminal, inittab_id, user_name, remote_host,
            process_finish_code, process_exit_code, session_id, timestamp, timestamp_microsec,
            a0, a1, a2, a3, reserved) = utmp.unpack(chunk)

        return cls(
            UTMPTypeMap(registry_type), pid, user_terminal, inittab_id, user_name, remote_host,
            process_finish_code, process_exit_code, session_id, timestamp, timestamp_microsec,
            (a0, a1, a2, a3), reserved,
        )


class UTMPDecodedData:
    registry_type: UTMPTypeMap
    pid: int
    user_terminal: str
    inittab_id: str
    user_name: str
    remote_hosts: List[str]
    process_finish_code: int
    process_exit_code: int
    session_id: int 
    timestamp: int
    timestamp_microsec: int
    remote_addr: str
    reserved: List[str]
    at: datetime


class LastLogin:
    user: str
    service: str
    login: str
    logout: str
    tty: str
    hostname: str
