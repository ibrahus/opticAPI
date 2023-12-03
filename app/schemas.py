from pydantic import BaseModel

class DeviceInfo(BaseModel):
    device_name: str = None
    device_id: str = None
