from pydantic import BaseModel, Field

class DeviceInfo(BaseModel):
    device_name: str = Field(None, alias='deviceName')
    device_id: str = Field(None, alias='deviceId')
