This repository provides a specialized bridge for users operating within the MiOS/VERA Home ecosystem. The application monitors the state of Zigbee sensors and switches connected to a MiOS gateway and translates these events into HTTP requests. This allows for real-time mobile notifications and local automation triggers on Android devices without relying on third-party cloud latency.

**Module Functions and Docker Architecture**
*   **MiOS Integration Module:** Interfaces with the local MiOS API to poll or receive push updates from your VERA controller.
*   **Event Dispatcher:** Filters raw gateway data to identify relevant state changes (e.g., motion detected, button pressed, contact opened).
*   **HTTP Client Wrapper:** Transmits refined event data to a configurable receiver IP/Port, specifically optimized for the Tasker HTTP Request event listener.
*   **Containerized Runtime:** A standalone Docker environment that ensures consistent execution across different host operating systems.
*   **Configuration Management:** Utilizes a centralized configuration file or environment variables to define gateway credentials and target client endpoints.
