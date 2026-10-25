# Switchboard AI 🚦

An intelligent query router that automatically optimizes your data workloads by routing lightweight queries to a local embedded engine (`DuckDB`) and heavy workloads to cloud warehouses (`Snowflake`).

## Features
- **Smart Routing:** Intercepts SQL queries and decides the most cost-effective compute engine.
- **Low Latency:** Executes minor lookups locally in-memory.
- **Seamless Snowflake Integration:** Native fallback to Snowflake cloud instances for heavy pipelines.

## Installation
```bash
pip install -e .