This repository provides a specialized bridge for users operating within the MiOS/VERA Home ecosystem. The application monitors the state of Z-wave sensors and switches connected to a MiOS gateway and translates these events into HTTP requests. This allows for real-time mobile notifications and local automation triggers on Android devices without relying on third-party cloud latency.

**Module Functions and Docker Architecture**
*   **MiOS Integration Module:** Interfaces with the local MiOS API to poll or receive push updates from your VERA controller.
*   **Event Dispatcher:** Filters raw gateway data to identify relevant state changes (e.g., motion detected, button pressed, contact opened).
*   **HTTP Client Wrapper:** Transmits refined event data to a configurable receiver IP/Port, specifically optimized for the Tasker HTTP Request event listener.
*   **Containerized Runtime:** A standalone Docker environment that ensures consistent execution across different host operating systems.
*   **Configuration Management:** Utilizes a centralized configuration file or environment variables to define gateway credentials and target client endpoints.


**Example LUA for 192.168.2.100**

**In your controller:**

Apps → Develop apps → Luup files




function statusChangedSwitch(device, service, variable, oldValue, newValue)
    local url = "http://192.168.2.100:1821/update?device=" .. device .. "&status=" .. newValue
    luup.inet.wget(url)
end

for device_id, device in pairs(luup.devices) do
    if luup.device_supports_service("urn:upnp-org:serviceId:SwitchPower1", device_id) then
        luup.variable_watch("statusChangedSwitch", "urn:upnp-org:serviceId:SwitchPower1", "Status", device_id)
    end
end

function statusChangedDimmer(device, service, variable, oldValue, newValue)
    local url = "http://192.168.2.100:1821/update?device=" .. device .. "&dimmer=" .. newValue
    luup.inet.wget(url)
end

for device_id, device in pairs(luup.devices) do
    if luup.device_supports_service("urn:upnp-org:serviceId:Dimming1", device_id) then
        luup.variable_watch("statusChangedDimmer", "urn:upnp-org:serviceId:Dimming1", "LoadLevelStatus", device_id)
    end
end

function statusChangedHumidity(device, service, variable, oldValue, newValue)
    local url = "http://192.168.2.100:1821/update?device=" .. device .. "&humidity=" .. newValue
    luup.inet.wget(url)
end

for device_id, device in pairs(luup.devices) do
    if luup.device_supports_service("urn:micasaverde-com:serviceId:HumiditySensor1", device_id) then
        luup.variable_watch("statusChangedHumidity", "urn:micasaverde-com:serviceId:HumiditySensor1", "CurrentLevel", device_id)
    end
end

function statusChangedTemperature(device, service, variable, oldValue, newValue)
    local url = "http://192.168.2.100:1821/update?device=" .. device .. "&temperature=" .. newValue
    luup.inet.wget(url)
end

for device_id, device in pairs(luup.devices) do
    if luup.device_supports_service("urn:upnp-org:serviceId:TemperatureSensor1", device_id) then
        luup.variable_watch("statusChangedTemperature", "urn:upnp-org:serviceId:TemperatureSensor1", "CurrentTemperature", device_id)
    end
end

function statusChangedDoor(device, service, variable, oldValue, newValue)
    local url = "http://192.168.2.100:1821/update?device=" .. device .. "&door_status=" .. newValue
    luup.inet.wget(url)
end

for device_id, device in pairs(luup.devices) do
    if luup.device_supports_service("urn:micasaverde-com:serviceId:SecuritySensor1", device_id) then
        luup.variable_watch("statusChangedDoor", "urn:micasaverde-com:serviceId:SecuritySensor1", "Tripped", device_id)
    end
end

