from enum import Enum, unique
from dataclasses import dataclass, field
import collections
import sys
import json


@unique
class MsgType(Enum):
    EV_UNITCONTROLSTATUS = 4
    EV_UNITDIMSTATUS = 5
    EV_UNITSWITCHSTATUS = 6
    EV_UNITSENSSTATUS = 7
    EV_MESSAGEERROR = 17
    EV_NODERESET = 18
    EV_UNITAUDIOSTATUS = 23
    EV_UNITDUOSWITCHSTATUS = 38
    EV_UNITAVMATRIXSTATUS = 54
    EV_UNITDEFAULTSTATUS = 48
    EV_NODEDATABASEINFO = 64
    EV_APPLICATIONTASKSTATUS = 66
    EV_CLIENTCONNECTSET = 67
    EV_UNITMACROCOMMAND = 69
    EV_UNITAUDIOEXTSTATUS = 70
    EV_TIMEDATESTATUS = 71
    EV_HEARTBEATSTATUS = 72
    EV_SCHEDULESTATUS = 73
    EV_NODEMANAGEMENTINFO = 74
    EV_ACCESSLEVELSET = 75
    EV_VIDEOPHONESTATUS = 76
    EV_REGISTERMAP = 77
    FC_UNITDIMREQUESTSTATUS = 131
    FC_UNITSENSSET = 136
    FC_UNITREQUESTSENSSTATUS = 137
    FC_NODERESETSET = 155
    FC_UNITAUDIOBASICSET = 159
    FC_UNITDIMSET = 162
    FC_UNITSWITCHSET = 163
    FC_UNITCONTROLSET = 168
    FC_TIMEDATE = 170
    FC_UNITIRTXSET = 173
    FC_UNITDUOSWITCHSET = 182
    FC_CHECKIRRXCODE = 192
    FC_UNITVIDEOMUXSET = 193
    FC_UNITAVMATRIXSET = 202
    FC_UNITALARMSET = 204
    FC_UNITAUDIOEXTSET = 208
    FC_NODEDATABASEREQUESTSTATUS = 209
    FC_APPLICATIONTASKSET = 212
    FC_REQUESTAPPLICATIONTASKSTATUS = 213
    FC_CLIENTCONNECTSET = 214
    FC_HEARTBEATREQUESTSTATUS = 215
    FC_REQUESTTIMEDATE = 216
    FC_SCHEDULESET = 217
    FC_REQUESTSCHEDULE = 218
    FC_NODEMANAGEMENTSET = 219
    FC_REQUESTNODEMANAGEMENT = 220
    FC_NODEDATABASESET = 221
    FC_ACCESSLEVELSET = 222
    FC_VIDEOPHONESET = 223
    FC_REGISTERMAP = 224


@dataclass
class Packet:
    """Basic structure for a packet."""

    cmdName: str = field(init=False)
    cmdCode: int = field(repr=False)
    method: int
    data: collections.deque
    cls: type = field(init=False)

    def __post_init__(self):
        """fill in the command nae, make the subsclass."""
        self.cmdName = MsgType(self.cmdCode)
        self.data = collections.deque(self.data)
        tmp = getattr(
            sys.modules[__name__], f"{MsgType(self.cmdCode).name}_{self.method}", None
        )
        if tmp:
            self.cls = tmp(self.data)
        else:
            self.cls = None


class BaseMessage:
    def __init__(self, data) -> None:
        pass

    def to_json(self) -> str:
        return json.dumps(self.to_json_basic())

    def to_json_basic(self) -> dict:
        """
        Create JSON structure with generic attributes
        """
        me = {}
        me["name"] = str(self.__class__.__name__)
        me.update(self.__dict__.copy())
        for key in me.copy():
            if key == "name":
                continue
            if callable(getattr(self, key)) or key.startswith("__"):
                del me[key]
            if isinstance(me[key], (bytes, bytearray)):
                me[key] = str(me[key], "utf-8")
        return me

    def __repr__(self) -> str:
        return self.to_json()


class BaseNodeUnitMessage(BaseMessage):
    nodeId: int
    unitId: int
    unitType: int

    def __init__(self, data):
        super().__init__(data)
        self.nodeId = data.popleft()
        self.unitId = data.popleft()
        self.unitType = data.popleft()


class EV_CLIENTCONNECTSET_3(BaseMessage):
    loginOk: bool

    def __init__(self, data):
        self.loginOK = data.popleft()


class EV_NODEDATABASEINFO_0(BaseMessage):
    numNode: int

    def __init__(self, data):
        self.numNode = data.popleft()


@unique
class NodeType(Enum):
    Standard = 1
    Gateway = 4
    Modem = 8
    Gui = 32


class EV_NODEDATABASEINFO_1(BaseMessage):
    index: int
    address: int
    nodeName: str
    numUnits: int
    nodeType: int
    nodeTypeName: NodeType
    flags: int

    def __init__(self, data):
        self.index = data.popleft()
        self.address = data.popleft()
        # next 4 are no needed
        [data.popleft() for _i in range(4)]
        self.nodeName = "".join([chr(data.popleft()) for _i in range(data.popleft())])
        self.numUnits = data.popleft()
        self.nodeType = data.popleft()
        self.nodeTypeName = NodeType(self.nodeType).name
        self.flags = data.popleft()


@unique
class UnitType(Enum):
    DIM = 1
    SWITCH = 2
    CONTROL = 3
    SEND = 4
    AUDIO_EXT = 5
    VIRTUAL = 7
    DUOSWITCH = 8
    AUDIO_BASIC = 10
    AVMATRIC = 11
    IRTX = 12
    VIDEOMUX = 14


class EV_NODEDATABASEINFO_2(BaseMessage):
    address: int
    unit: int
    laddress: int
    lunit: int
    unitName: str
    unitType: int
    unitTypeName: UnitType
    unitFlags: int

    def __init__(self, data):
        self.address = data.popleft()
        self.unit = data.popleft()
        self.laddress = data.popleft()
        self.lunit = data.popleft()
        self.unitName = "".join([chr(data.popleft()) for _i in range(data.popleft())])
        self.unitType = data.popleft()
        self.unitTypeName = UnitType(self.unitType).name
        self.unitFlags = data.popleft()


class EV_UNITSENSSTATUS_0(BaseNodeUnitMessage):
    controlState: int
    state: int
    preset: int

    def __init__(self, data) -> None:
        super().__init__(data)
        self.controlState = data.popleft()
        self.state = data.popleft()
        self.preset = data.popleft()


class EV_UNITSENSSTATUS_1(EV_UNITSENSSTATUS_0):
    def __init__(self, data) -> None:
        super().__init__(data)


class EV_UNITDIMSTATUS_0(BaseNodeUnitMessage):
    state: int
    dimValue: int

    def __init__(self, data) -> None:
        super().__init__(data)
        # config, reserved
        data.popleft()
        self.state = data.popleft()
        self.dimValue = data.popleft()
