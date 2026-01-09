
import pytest
import sys
import os
import xml.etree.ElementTree as ET
import time
import platform
import datetime

def run_tests_and_report():
    """
    Runs pytest, generates a JUnit XML report, and if failures occur,
    parse the XML to create a detailed markdown report for the user.
    """
    report_file = "test_report.xml"
    
    # Remove old report if exists
    if os.path.exists(report_file):
        os.remove(report_file)

    print("🚀 Starting comprehensive test suite execution...")
    start_time = time.time()
    
    # Run pytest
    # -x: stop on first failure (optional, maybe better to run all) -> decided to run all
    # --junitxml: generate XML report
    # -o junit_family=xunit2: standard format
    # -o junit_logging=all: capture stdout/stderr in the report
    exit_code = pytest.main(["tests/", f"--junitxml={report_file}", "-v", "-o", "junit_family=xunit2", "-o", "junit_logging=all"])
    
    duration = time.time() - start_time
    print(f"\n⏱️  Tests finished in {duration:.2f} seconds.")

    # Even if tests pass, we might want to see the report if the user asked for it, 
    # but strictly speaking we only need to generate it on failure or request.
    # Here we generate it always for visibility, or at least if there are non-passed tests.
    
    generate_markdown_report(report_file, duration)
    
    return exit_code

def generate_markdown_report(xml_file, duration):
    """Parses JUnit XML and creates a Markdown summary"""
    if not os.path.exists(xml_file):
        print("⚠️ No XML report file found. Pytest might have failed to start.")
        return

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # In xunit2, <testsuites> is root, containing <testsuite>. 
        # But pytest often outputs just <testsuite> as root depending on config.
        # Let's handle both.
        testsuites = [root] if root.tag == "testsuite" else root.findall("testsuite")
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0
        
        failures = []
        errors = []
        skipped = []
        passed = []

        for suite in testsuites:
            total_tests += int(suite.get("tests", 0))
            total_failures += int(suite.get("failures", 0))
            total_errors += int(suite.get("errors", 0))
            total_skipped += int(suite.get("skipped", 0))

            for testcase in suite.iter("testcase"):
                name = testcase.get("name")
                classname = testcase.get("classname")
                file_path = testcase.get("file")
                full_name = f"{classname}.{name}"
                
                # Check outcome
                failure = testcase.find("failure")
                error = testcase.find("error")
                skip = testcase.find("skipped")
                
                if failure is not None:
                    failures.append({
                        "name": name,
                        "classname": classname,
                        "file": file_path,
                        "message": failure.get("message"),
                        "text": failure.text,
                        "type": "FAILURE"
                    })
                elif error is not None:
                    errors.append({
                        "name": name,
                        "classname": classname,
                        "file": file_path,
                        "message": error.get("message"),
                        "text": error.text,
                        "type": "ERROR"
                    })
                elif skip is not None:
                    skipped.append({
                        "name": name,
                        "classname": classname,
                        "message": skip.get("message"),
                        "type": "SKIPPED"
                    })
                else:
                    passed.append({
                        "name": name,
                        "classname": classname,
                        "time": testcase.get("time"),
                        "type": "PASSED"
                    })

        # Calculate pass rate
        pass_count = total_tests - total_failures - total_errors - total_skipped
        pass_rate = (pass_count / total_tests * 100) if total_tests > 0 else 0
        
        # Build Report
        lines = []
        lines.append(f"# 🧪 Test Execution Report")
        lines.append(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Environment:** Python {platform.python_version()} on {platform.system()}")
        lines.append("")
        
        # Summary Table
        lines.append("## 📊 Summary")
        lines.append("| Metric | Count |")
        lines.append("| :--- | :--- |")
        lines.append(f"| **Total Tests** | {total_tests} |")
        lines.append(f"| ✅ **Passed** | {pass_count} |")
        lines.append(f"| ❌ **Failed** | {total_failures} |")
        lines.append(f"| ⚠️ **Errors** | {total_errors} |")
        lines.append(f"| ⏭️ **Skipped** | {total_skipped} |")
        lines.append(f"| ⏱️ **Duration** | {duration:.2f}s |")
        lines.append(f"| **Pass Rate** | {pass_rate:.1f}% |")
        lines.append("")

        if failures or errors:
            lines.append("## 🚨 Failures & Errors")
            lines.append("> Use the details below to debug the issues.")
            lines.append("")
            
            for item in failures + errors:
                icon = "❌" if item["type"] == "FAILURE" else "⚠️"
                lines.append(f"### {icon} {item['classname']}: `{item['name']}`")
                lines.append(f"- **File:** `{item['file']}`")
                if item['message']:
                     lines.append(f"- **Message:** `{item['message']}`")
                
                lines.append("<details><summary><b>Stack Trace / Details</b></summary>")
                lines.append("")
                lines.append("```python")
                lines.append(item['text'] if item['text'] else "No details captured.")
                lines.append("```")
                lines.append("")
                lines.append("</details>")
                lines.append("")
                
                # Heuristic Analysis
                lines.append("**💡 Potential Fix:**")
                msg = (item['message'] or "").lower()
                text = (item['text'] or "").lower()
                
                if "404" in msg or "404" in text:
                    lines.append("- **404 Not Found**: Resource likely missing. Check initialization logic or ID mismatches.")
                elif "403" in msg or "403" in text:
                    lines.append("- **403 Forbidden**: Permission issue. Check user roles and token validity.")
                elif "401" in msg or "401" in text:
                    lines.append("- **401 Unauthorized**: Authentication failed. Check login/token logic.")
                elif "keyerror" in msg or "keyerror" in text:
                    lines.append("- **KeyError**: Response JSON is missing expected keys. Debug API response structure.")
                elif "assertionerror" in msg or "assertionerror" in text:
                    lines.append("- **AssertionError**: Value mismatch. Compare expected vs actual.")
                else:
                    lines.append("- Review the stack trace above to identify the root cause.")
                lines.append("---")

        output_path = "TEST_FAILURE_REPORT.md"
        with open(output_path, "w") as f:
            f.write("\n".join(lines))
            
        print(f"📄 Detailed report generated at: {os.path.abspath(output_path)}")

    except Exception as e:
        print(f"Failed to generate report: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    sys.exit(run_tests_and_report())
