# GitHub Actions Workflow Maintenance Guide

## Overview

This guide provides comprehensive instructions for maintaining and monitoring the GitHub Actions workflows for the pAIssive Income project, particularly following the successful resolution of PR #139 workflow issues.

## 🔍 Daily Monitoring

### Workflow Health Checks
```bash
# Check workflow status using GitHub CLI
gh run list --limit 10 --json status,conclusion,name

# Monitor specific workflow
gh run list --workflow="consolidated-ci-cd.yml" --limit 5
```

### Key Metrics to Monitor
- **Success Rate**: Should maintain >95% success rate
- **Execution Time**: Monitor for performance degradation
- **Coverage Trends**: Ensure coverage stays above 15% threshold
- **Security Alerts**: Check for new vulnerabilities

## 🛠️ Routine Maintenance Tasks

### Weekly Tasks
1. **Review Failed Workflows**
   - Investigate any failures in the past week
   - Update documentation if new issues are discovered
   - Apply fixes promptly to prevent accumulation

2. **Dependency Updates**
   - Check for security updates in requirements-ci.txt
   - Update GitHub Actions to latest versions
   - Test changes locally with act before deployment

3. **Coverage Analysis**
   - Review Codecov reports for coverage trends
   - Identify areas needing additional test coverage
   - Plan coverage improvement initiatives

### Monthly Tasks
1. **Performance Review**
   - Analyze workflow execution times
   - Identify optimization opportunities
   - Update timeout configurations if needed

2. **Security Audit**
   - Review security scan results
   - Update security tool configurations
   - Address any new security recommendations

3. **Documentation Updates**
   - Update workflow documentation for any changes
   - Review and update troubleshooting guides
   - Ensure maintenance procedures are current

## 🚨 Troubleshooting Common Issues

### Workflow Timeout Issues
**Symptoms**: Workflows failing due to timeout
**Solution**:
```yaml
# Update timeout in workflow file
timeout-minutes: 75  # Increase as needed
```

### Dependency Installation Failures
**Symptoms**: pip/uv installation errors
**Solution**:
1. Check requirements-ci.txt for conflicts
2. Update pinned versions
3. Test locally with act

### Test Collection Errors
**Symptoms**: pytest collection failures
**Solution**:
1. Check for new broken symlinks
2. Update test exclusions in pytest.ini
3. Verify PYTHONPATH configuration

### Coverage Threshold Failures
**Symptoms**: Coverage below 15% threshold
**Solution**:
1. Review coverage reports
2. Add tests for uncovered code
3. Update coverage exclusions if appropriate

## 📊 Performance Optimization

### Caching Strategies
```yaml
# Python dependencies caching
- name: Cache Python dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('requirements-ci.txt') }}

# Node.js dependencies caching
- name: Cache pnpm dependencies
  uses: actions/cache@v4
  with:
    path: ~/.pnpm-store
    key: ${{ runner.os }}-pnpm-${{ hashFiles('ui/react_frontend/pnpm-lock.yaml') }}
```

### Parallel Execution
- Use matrix strategies for multi-platform testing
- Implement job dependencies to optimize execution order
- Consider splitting large test suites

## 🔧 Configuration Management

### Environment Variables
```yaml
# Standard environment variables for workflows
env:
  PYTHONPATH: ${{ github.workspace }}
  CI: true
  GITHUB_ACTIONS: true
```

### Secrets Management
- Regularly rotate secrets and tokens
- Use GitHub's secret scanning features
- Implement least-privilege access principles

## 📈 Continuous Improvement

### Metrics Collection
1. **Workflow Success Rates**
   - Track success/failure rates over time
   - Identify patterns in failures
   - Set up alerts for degradation

2. **Performance Metrics**
   - Monitor execution times
   - Track resource usage
   - Identify bottlenecks

3. **Coverage Trends**
   - Monitor test coverage over time
   - Set goals for coverage improvement
   - Track coverage by module/component

### Automation Opportunities
1. **Dependency Updates**
   - Implement Dependabot for automated updates
   - Set up automated security patch application
   - Create automated testing for dependency updates

2. **Workflow Optimization**
   - Implement dynamic timeout adjustment
   - Add intelligent test selection
   - Optimize caching strategies

## 🚀 Deployment Best Practices

### Pre-Deployment Checklist
- [ ] Test workflow changes locally with act
- [ ] Verify all required secrets are available
- [ ] Check for breaking changes in dependencies
- [ ] Update documentation for any changes
- [ ] Review security implications

### Post-Deployment Monitoring
- Monitor first few runs after deployment
- Check for any new error patterns
- Verify performance hasn't degraded
- Update monitoring dashboards

## 📞 Escalation Procedures

### When to Escalate
1. **Critical Failures**: Workflows blocking deployments
2. **Security Issues**: New vulnerabilities discovered
3. **Performance Degradation**: Significant slowdowns
4. **Repeated Failures**: Same issue occurring multiple times

### Escalation Steps
1. Document the issue thoroughly
2. Gather relevant logs and error messages
3. Check existing documentation and troubleshooting guides
4. Create GitHub issue with detailed information
5. Notify team leads if blocking critical operations

## 📚 Resources and References

### Documentation Links
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Act Local Testing Tool](https://github.com/nektos/act)
- [Codecov Documentation](https://docs.codecov.com/)
- [Project CI/CD Documentation](02_github_actions.md)

### Useful Commands
```bash
# Test consolidated workflow locally (dry run)
act -j lint-test --platform ubuntu-latest=ubuntu:latest --dryrun
act -j security --platform ubuntu-latest=ubuntu:latest --dryrun

# Test enhanced CI wrapper locally
python run_tests_ci_wrapper_enhanced.py

# Test security fallback creation
python scripts/security/create_security_fallbacks.py

# Check workflow syntax and structure
act --list

# Run specific job with platform specification
act -j lint-test --platform ubuntu-latest=ubuntu:latest
act -j security --platform ubuntu-latest=ubuntu:latest

# Monitor workflow execution times
gh run list --workflow="consolidated-ci-cd.yml" --limit 10 --json status,conclusion,createdAt,updatedAt
```

### Contact Information
- **Primary Maintainer**: Development Team
- **Documentation**: docs/03_devops_and_cicd/
- **Issue Tracking**: GitHub Issues
- **Emergency Contact**: Team Leads

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 2024 | Initial maintenance guide creation |
| 1.1 | Dec 2024 | Updated for consolidated CI/CD workflow and enhanced testing infrastructure |

### Recent Updates (v1.1)
- **Consolidated Workflow**: Updated commands and procedures for single `consolidated-ci-cd.yml` workflow
- **Enhanced CI Wrapper**: Added documentation for `run_tests_ci_wrapper_enhanced.py` testing
- **Security Infrastructure**: Included security fallback script testing and monitoring
- **Local Testing**: Enhanced act tool usage with platform-specific testing
- **Cross-Platform Support**: Added guidance for Ubuntu, Windows, and macOS workflow management

---

*This guide should be reviewed and updated quarterly to ensure accuracy and relevance.*
