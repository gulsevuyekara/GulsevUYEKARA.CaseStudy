from locust import HttpUser, task, between
import time
test_results = []

TEST_CASES = [
    {"id": 1, "name": "Single Keyword Search", "url": "/arama?q=laptop"},
    {"id": 2, "name": "Multi Keyword Search", "url": "/arama?q=laptop+kamera"},
    {"id": 3, "name": "Empty Search", "url": "/arama?q="},
    {"id": 4, "name": "Gibberish Characters Search", "url": "/arama?q=½{[[[=?"},
    {"id": 5, "name": "Extremely Long Keyword Search", "url": "/arama?q=" + "abc+%/?"*500},
    {"id": 6, "name": "Complex Filter Search – Low Results",
     "url": "/arama?q=kamera&minp=100&maxp=3000&m=Cbtx+Global-Butu-Prestigegoods-Soulader&iw=tablet_aksesuar"},
    {"id": 7, "name": "Complex Filter Search – High Results",
     "url": "/arama?q=çocuk&minp=100&maxp=10000&isf=1&isagt=3_2&kumasturu=...&cns=Kız+Çocuk-Unisex-Erkek+Çocuk&beden=4_5+Yaş-27_30-4-5&hdfl=cats_cns_kumasturu_beden_yka_shpms_ppf"},
    {"id": 8, "name": "Filter Removal (Sub-Search / Filtered Pages)",
     "url": "/arama?q=çocuk&isagt=2&hdfl=cats_cns_kumasturu_beden_yka_shpms_ppf"},
    {"id": 9, "name": "Autocomplete Search - doğ", "url": "/arama/tamamla?keyword=doğ"},
    {"id": 10, "name": "Autocomplete Search - can", "url": "/arama/tamamla?keyword=can"},
    {"id": 11, "name": "Search with Price Range Filter", "url": "/arama?q=telefon&minp=1000&maxp=10000"},
    {"id": 12, "name": "Network Fail Simulation", "url": "/arama?q=laptop", "simulate_fail": True},
    {"id": 13, "name": "Low Timeout Simulation", "url": "/arama?q=laptop", "timeout": 0.5}
]

class WebsiteUser(HttpUser):
    host = "https://www.n11.com"
    wait_time = between(1, 2)

    @task
    def run_test_cases(self):
        for case in TEST_CASES:
            start = time.time()
            try:
                if case.get("simulate_fail"):
                    response = self.client.get(case["url"], timeout=0.001)
                else:
                    timeout = case.get("timeout", 10)
                    response = self.client.get(case["url"], timeout=timeout)

                duration = time.time() - start
                status = response.status_code
                success = status == 200
            except Exception:
                duration = time.time() - start
                status = None
                success = False

            test_results.append({
                "TC ID": case["id"],
                "Test Case": case["name"],
                "URL": case["url"],
                "Status Code": status,
                "Success": success,
                "Duration (s)": round(duration, 2)
            })
