# Kostal Smartmeter and Enector Integration for Home Assistant

[![Static Badge](https://img.shields.io/badge/HACS-Custom-41BDF5?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=white)](https://github.com/hacs/integration) 
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/MeisterTR/ha-kostal-smartmeter/total?style=for-the-badge)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/MeisterTR/ha-kostal-smartmeter?style=for-the-badge)

![GitHub Release Date](https://img.shields.io/github/release-date-pre/MeisterTR/ha-kostal-smartmeter?style=for-the-badge&label=Latest%20Beta%20Release) [![GitHub Release](https://img.shields.io/github/v/release/MeisterTR/ha-kostal-smartmeter?include_prereleases&style=for-the-badge)](https://github.com/MeisterTR/ha-kostal-smartmeter/releases)

![GitHub Release Date](https://img.shields.io/github/release-date/MeisterTR/ha-kostal-smartmeter?style=for-the-badge&label=Latest%20Release) [![GitHub Release](https://img.shields.io/github/v/release/MeisterTR/ha-kostal-smartmeter?style=for-the-badge)](https://github.com/MeisterTR/ha-kostal-smartmeter/releases)


---
## 📁 Installation

### 📦 HACS (custom repository)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=MeisterTR&repository=ha-kostal-smartmeter&category=Integration)

### 🧰 Manual Installation (alternative)

1. Download this repository as ZIP or clone it.  
2. Copy the folder `custom_components/ksem/` into your Home Assistant config directory:  

## 🔧 Purpose

The **KSEM Smartmeter Integration** enables seamless integration of the **KOSTAL Smart Energy Meter (KSEM)** and connected **Kostal Enector wallboxes** into Home Assistant.  

This custom component provides **local access** to real-time energy and charging data via the **built-in REST API** and **WebSocket interfaces** – without any dependency on the cloud.  

With this integration you can:  
- Monitor **live charging data**, grid consumption, PV production, and household energy usage  
- Control **charging modes** (e.g. solar-only, grid, hybrid, locked)  
- Switch between **1-phase, 3-phase, or automatic** charging  
- Set **minimum PV / charging quotas** and manage load balancing  
- Expose all values to Home Assistant’s **energy dashboard**, automations, and scripts  

This makes it possible to build advanced automations such as:  
- Charging your EV only with PV surplus  
- Prioritizing house or battery consumption before charging the car  
- Dynamically adjusting charging power based on current load  
- Using Tibber or other dynamic tariffs to optimize charging costs  

In short: **complete local control and monitoring of your KSEM and wallbox directly in Home Assistant.**  

---

## 🚀 Features

- ✅ Local authentication with password  
- ✅ REST API communication for configuration and status  
- ✅ WebSocket subscription for live charging data  
- ✅ Sensor entities:  
  - Charging state, phases, current, voltage, power  
  - Wallbox device info  
  - Energy and load data  
- ✅ Control entities:  
  - Charging mode (`net`, `pv`, `hybrid`, `locked`)  
  - Phase switching (`1-phase`, `3-phase`, `auto`)  
  - Battery usage toggle  
  - Minimum PV / charging power quota (adjustable)  
- 🔄 Automatic updates from WebSocket for live control values  
- 🔜 Future: Energy dashboard support  

---


```text
MIT License

Copyright (c) 2025 MeisterTR

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.