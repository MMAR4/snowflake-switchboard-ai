import json
from snowflake.snowpark import Session
from snowflake.snowpark.dataframe import DataFrame

class MultiTierSwitchboard:
    def __init__(self, session: Session, warehouses: list = None, tiers: list = None):
        self.session = session
        
        if tiers:
            self.tiers = sorted(tiers, key=lambda x: x["max_bytes"])
        elif warehouses:
            standard_limits = [
                1_000_000_000,      # 1 GB (XS limit)
                5_000_000_000,      # 5 GB (Small limit)
                20_000_000_000,     # 20 GB (Medium limit)
                50_000_000_000,     # 50 GB (Large limit)
                100_000_000_000,    # 100 GB (X-Large limit)
                500_000_000_000     # 500 GB (2X-Large limit)
            ]
            self.tiers = []
            for i, wh in enumerate(warehouses):
                if i == len(warehouses) - 1:
                    limit = float("inf")
                else:
                    limit = standard_limits[i] if i < len(standard_limits) else float("inf")
                self.tiers.append({"warehouse": wh, "max_bytes": limit})
        else:
            self.tiers = [
                {"warehouse": "COMPUTE_WH", "max_bytes": 1_000_000_000},
                {"warehouse": "PRACTICE", "max_bytes": float("inf")}
            ]

    def run(self, query: str) -> DataFrame:
        print(f"🤖 [Switchboard AI]: Analyzing query structure...")
        
        estimated_bytes = 0
        try:
            explain_sql = f"SELECT SYSTEM$EXPLAIN_PLAN_JSON($${query}$$)"
            explain_result = self.session.sql(explain_sql).collect()
            plan_json_str = explain_result[0][0]
            
            if plan_json_str:
                plan_data = json.loads(plan_json_str)
                estimated_bytes = self._extract_bytes_assigned(plan_data)
                
            print(f"📊 [Switchboard AI]: Estimated telemetry payload -> {estimated_bytes:,} bytes assigned.")
            
        except Exception as e:
            print(f"⚠️ [Switchboard AI]: Pre-check skipped ({e}). Using baseline tier.")

        target_wh = self.tiers[0]["warehouse"]
        for tier in self.tiers:
            if estimated_bytes <= tier["max_bytes"]:
                target_wh = tier["warehouse"]
                break

        print(f"🚀 [Switchboard AI]: Routing query to optimal tier -> {target_wh}")

        self.session.sql(f"USE WAREHOUSE {target_wh}").collect()
        
        print(f"⚙️ [Switchboard AI]: Executing query...")
        return self.session.sql(query)

    def __call__(self, query: str, auto_show: bool = True) -> DataFrame:
        df = self.run(query)
        if auto_show:
            df.show()
        return df

    def _extract_bytes_assigned(self, plan_node) -> int:
        total_bytes = 0
        if isinstance(plan_node, dict):
            if "bytesAssigned" in plan_node:
                try:
                    total_bytes += int(plan_node["bytesAssigned"])
                except (ValueError, TypeError):
                    pass
            for key, value in plan_node.items():
                total_bytes += self._extract_bytes_assigned(value)
        elif isinstance(plan_node, list):
            for item in plan_node:
                total_bytes += self._extract_bytes_assigned(item)
        return total_bytes