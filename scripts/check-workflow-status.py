#!/usr/bin/env python3
"""
Workflow Status Checker

This script analyzes GitHub Actions workflows to identify potential issues
and provide troubleshooting recommendations.
"""

import glob
import os
from typing import Any, Dict, List

import yaml


class WorkflowAnalyzer:
    def __init__(self, workflows_dir: str = ".github/workflows"):
        self.workflows_dir = workflows_dir
        self.issues = []
        self.warnings = []
        self.recommendations = []

    def analyze_all_workflows(self) -> Dict[str, Any]:
        """Analyze all workflow files and return comprehensive report."""
        print("🔍 Analyzing GitHub Actions workflows...")

        workflow_files = glob.glob(f"{self.workflows_dir}/*.yml")

        results = {
            "total_files": len(workflow_files),
            "valid_files": 0,
            "invalid_files": 0,
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "file_analysis": {},
        }

        for workflow_file in workflow_files:
            file_result = self.analyze_workflow_file(workflow_file)
            results["file_analysis"][workflow_file] = file_result

            if file_result["valid"]:
                results["valid_files"] += 1
            else:
                results["invalid_files"] += 1

        # Perform cross-workflow analysis
        self.analyze_workflow_conflicts(workflow_files)

        results["issues"] = self.issues
        results["warnings"] = self.warnings
        results["recommendations"] = self.recommendations

        return results

    def analyze_workflow_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single workflow file."""
        result = {
            "valid": False,
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "structure": {},
        }

        try:
            with open(file_path, encoding="utf-8") as f:
                content = yaml.safe_load(f)

            if content is None:
                result["issues"].append("Empty or invalid YAML content")
                return result

            result["valid"] = True
            result["structure"] = self.analyze_workflow_structure(content, file_path)

        except yaml.YAMLError as e:
            result["issues"].append(f"YAML syntax error: {e}")
        except Exception as e:
            result["issues"].append(f"Error reading file: {e}")

        return result

    def analyze_workflow_structure(
        self, workflow: Dict[str, Any], file_path: str
    ) -> Dict[str, Any]:
        """Analyze the structure of a workflow."""
        structure = {
            "has_name": "name" in workflow,
            "has_on": "on" in workflow,
            "has_jobs": "jobs" in workflow,
            "job_count": 0,
            "uses_timeouts": False,
            "uses_concurrency": False,
            "uses_continue_on_error": False,
            "action_versions": [],
        }

        # Check required fields
        if not structure["has_name"]:
            self.issues.append(f"{file_path}: Missing 'name' field")
        if not structure["has_on"]:
            self.issues.append(f"{file_path}: Missing 'on' field")
        if not structure["has_jobs"]:
            self.issues.append(f"{file_path}: Missing 'jobs' field")

        # Analyze jobs
        if "jobs" in workflow:
            jobs = workflow["jobs"]
            structure["job_count"] = len(jobs)

            for job_name, job_config in jobs.items():
                # Check for timeouts
                if "timeout-minutes" in job_config:
                    structure["uses_timeouts"] = True
                else:
                    self.warnings.append(
                        f"{file_path}: Job '{job_name}' missing timeout"
                    )

                # Check for continue-on-error usage
                if "continue-on-error" in job_config:
                    structure["uses_continue_on_error"] = True
                    self.warnings.append(
                        f"{file_path}: Job '{job_name}' uses continue-on-error"
                    )

                # Analyze steps
                if "steps" in job_config:
                    for step in job_config["steps"]:
                        if "uses" in step:
                            action = step["uses"]
                            structure["action_versions"].append(action)
                            self.check_action_version(action, file_path)

                        if "continue-on-error" in step:
                            structure["uses_continue_on_error"] = True

        # Check for concurrency control
        if "concurrency" in workflow:
            structure["uses_concurrency"] = True
        else:
            self.recommendations.append(
                f"{file_path}: Consider adding concurrency control"
            )

        return structure

    def check_action_version(self, action: str, file_path: str):
        """Check if action versions are up to date."""
        version_recommendations = {
            "actions/checkout": "v4",
            "actions/setup-node": "v4",
            "actions/setup-python": "v5",
            "actions/cache": "v4",
            "actions/upload-artifact": "v4",
            "actions/download-artifact": "v4",
        }

        if "@" in action:
            action_name, version = action.split("@", 1)

            if action_name in version_recommendations:
                recommended = version_recommendations[action_name]
                if version != recommended:
                    self.recommendations.append(
                        f"{file_path}: Consider updating {action_name} from {version} to {recommended}"
                    )

    def analyze_workflow_conflicts(self, workflow_files: List[str]):
        """Analyze potential conflicts between workflows."""
        workflow_names = []
        trigger_analysis = {"push": [], "pull_request": [], "schedule": []}

        for file_path in workflow_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = yaml.safe_load(f)

                if content and "name" in content:
                    workflow_names.append(content["name"])

                if content and "on" in content:
                    triggers = content["on"]
                    if isinstance(triggers, dict) or isinstance(triggers, list):
                        for trigger in triggers:
                            if trigger in trigger_analysis:
                                trigger_analysis[trigger].append(file_path)

            except Exception:
                continue

        # Check for duplicate names
        seen_names = set()
        for name in workflow_names:
            if name in seen_names:
                self.issues.append(f"Duplicate workflow name: {name}")
            seen_names.add(name)

        # Check for too many concurrent triggers
        for trigger, files in trigger_analysis.items():
            if len(files) > 5:
                self.warnings.append(
                    f"Many workflows ({len(files)}) trigger on '{trigger}' - may cause resource conflicts"
                )

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive report."""
        report = []
        report.append("# GitHub Actions Workflow Analysis Report")
        report.append(f"Generated: {self.get_timestamp()}")
        report.append("")

        # Summary
        report.append("## Summary")
        report.append(f"- Total workflow files: {results['total_files']}")
        report.append(f"- Valid files: {results['valid_files']}")
        report.append(f"- Invalid files: {results['invalid_files']}")
        report.append(f"- Issues found: {len(results['issues'])}")
        report.append(f"- Warnings: {len(results['warnings'])}")
        report.append(f"- Recommendations: {len(results['recommendations'])}")
        report.append("")

        # Issues
        if results["issues"]:
            report.append("## 🚨 Issues (Must Fix)")
            for issue in results["issues"]:
                report.append(f"- ❌ {issue}")
            report.append("")

        # Warnings
        if results["warnings"]:
            report.append("## ⚠️ Warnings")
            for warning in results["warnings"]:
                report.append(f"- ⚠️ {warning}")
            report.append("")

        # Recommendations
        if results["recommendations"]:
            report.append("## 💡 Recommendations")
            for rec in results["recommendations"]:
                report.append(f"- 💡 {rec}")
            report.append("")

        # Troubleshooting guide
        report.append("## 🔧 Troubleshooting Guide")
        report.append("")
        report.append("### Common Issues and Solutions")
        report.append("")
        report.append("1. **YAML Syntax Errors**")
        report.append("   - Check for proper indentation (use spaces, not tabs)")
        report.append("   - Ensure colons are followed by spaces")
        report.append("   - Validate YAML syntax online or with yamllint")
        report.append("")
        report.append("2. **Action Version Issues**")
        report.append("   - Update to latest stable versions")
        report.append("   - Check GitHub Marketplace for version compatibility")
        report.append("")
        report.append("3. **Resource Conflicts**")
        report.append("   - Add concurrency groups to prevent parallel runs")
        report.append("   - Use `cancel-in-progress: true` for PR workflows")
        report.append("")
        report.append("4. **Timeout Issues**")
        report.append("   - Add `timeout-minutes` to all jobs")
        report.append("   - Set reasonable timeouts (5-30 minutes typically)")
        report.append("")
        report.append("5. **Environment Issues**")
        report.append("   - Ensure proper environment variable setup")
        report.append("   - Test cross-platform compatibility")
        report.append("")
        report.append("### Debug Commands")
        report.append("")
        report.append("To enable debug logging, add these environment variables:")
        report.append("```yaml")
        report.append("env:")
        report.append("  ACTIONS_RUNNER_DEBUG: true")
        report.append("  ACTIONS_STEP_DEBUG: true")
        report.append("```")
        report.append("")

        return "\n".join(report)

    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def main():
    """Main function to run workflow analysis."""
    analyzer = WorkflowAnalyzer()
    results = analyzer.analyze_all_workflows()

    # Generate and save report
    report = analyzer.generate_report(results)

    # Save to file
    os.makedirs("ci-reports", exist_ok=True)
    report_file = "ci-reports/workflow-analysis-report.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"📊 Analysis complete! Report saved to: {report_file}")

    # Print summary to console
    print("\n" + "=" * 50)
    print("WORKFLOW ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"Total files: {results['total_files']}")
    print(f"Valid files: {results['valid_files']}")
    print(f"Invalid files: {results['invalid_files']}")
    print(f"Issues: {len(results['issues'])}")
    print(f"Warnings: {len(results['warnings'])}")
    print(f"Recommendations: {len(results['recommendations'])}")

    if results["issues"]:
        print("\n🚨 CRITICAL ISSUES FOUND:")
        for issue in results["issues"][:5]:  # Show first 5
            print(f"  ❌ {issue}")
        if len(results["issues"]) > 5:
            print(f"  ... and {len(results['issues']) - 5} more")

    if results["invalid_files"] == 0 and len(results["issues"]) == 0:
        print("\n✅ All workflow files are valid!")
        return 0
    print(
        f"\n❌ Found {results['invalid_files']} invalid files and {len(results['issues'])} issues"
    )
    return 1


if __name__ == "__main__":
    exit(main())
