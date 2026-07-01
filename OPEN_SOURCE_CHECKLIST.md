# Open-Source Release Checklist

Before publishing this skill:

1. Remove private URLs, names, evidence files, and company-specific outputs.
2. Choose a license intentionally.
3. Run Python syntax checks:

   ```bash
   python3 -m py_compile scripts/collect_git.py scripts/render_report.py
   ```

4. Run a git-only smoke test on a disposable repo.
5. Verify these cases:
   - local commits without MR
   - pushed branch without MR
   - MR open but not merged
   - MR merged with dirty local worktree
   - inaccessible external source
   - custom template
   - multi-author repo with identity filtering
6. Confirm the default report does not include other people's fetched remote branches as the user's work.
7. Confirm evidence JSON is auditable but does not store source code or secrets.
8. Update README examples if script flags change.

