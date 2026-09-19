Phase 1 implementation is functionally complete but is still pending final release acceptance.

Current status:

* Final API image rebuilt successfully:

  * `sha256:62ae19d1…`
* Final Web image rebuilt successfully:

  * `sha256:22da5446…`
* Existing functional, integration, migration/restore, and production-smoke evidence is green.
* Final repository validation passed:

  * `git diff --check`
  * shell syntax validation
  * JSON validation
  * secret-pattern scan
  * floating-image-tag scan
* `docs/phase-1-results.md` has been updated with the rebuilt-image evidence and outstanding release gates.
* Phase 2 has NOT started.
* No commit or push has occurred yet.

Two release gates remain:

1. Final production-image vulnerability scan.
2. Hosted CI verification.

The previous vulnerability-scan attempts were blocked because:

* mounting the Docker socket into a floating external scanner container was rejected as too broad;
* the safer local Grype approach had a valid vulnerability database but could not finish Docker-image cataloging/export within the execution boundary.

Hosted CI cannot currently verify this work because the changes are uncommitted/unpushed, and the local `gh` credentials are invalid.

## OBJECTIVE

Create a safe Phase 1 candidate checkpoint, push it, use that pushed commit to obtain hosted CI evidence, and finish the remaining release-gate verification.

This commit is a review/release candidate checkpoint. Creating it does NOT by itself declare Phase 1 accepted.

Do NOT begin Phase 2.

---

## 1. PRE-COMMIT REVIEW

Before committing:

1. Run `git status`.
2. Review the complete diff.
3. Confirm there are no:

   * secrets
   * `.env` files containing credentials
   * temporary/debug files
   * logs
   * caches
   * local IDE artifacts
   * build outputs that should not be tracked
   * unrelated changes
4. Re-run:

   * `git diff --check`
   * relevant formatting/lint checks
   * generated API client drift check
   * shell syntax validation
   * JSON/config validation
   * secret-pattern scan
5. Confirm existing Phase 1 functional tests remain green.

If any of these checks fail, fix the issue before committing.

---

## 2. CREATE PHASE 1 CANDIDATE COMMIT

Stage only Phase 1 files.

Create a commit with a clear message such as:

`feat: complete phase 1 platform foundation`

Do NOT amend unrelated historical commits.

Record:

* current branch
* commit SHA
* commit message

---

## 3. PUSH

Push the current working branch to its configured remote.

Do not force-push.

If no upstream exists, establish the appropriate upstream for the current branch using the repository's normal workflow.

If push fails because of authentication or repository configuration, report the exact blocker and stop.

---

## 4. HOSTED CI

After the push succeeds, inspect the hosted CI run triggered by this exact commit.

Do not rely on local `gh` authentication if it is unavailable.

Use the safest repository-supported method available to verify the CI state.

Confirm the status of every required workflow/job relevant to Phase 1.

Record:

* commit SHA
* workflow/run identifier if available
* each required job
* pass/fail/cancelled/skipped status
* any failure details

Do not treat skipped required jobs as passing unless the workflow intentionally specifies that behavior.

If hosted CI fails:

1. identify the failure;
2. fix it;
3. rerun the relevant local checks;
4. commit the correction;
5. push;
6. verify hosted CI again.

Keep Phase 2 blocked until required hosted CI is green.

---

## 5. VULNERABILITY SCAN

Complete the final scan against the exact production API and Web images corresponding to the candidate commit.

Do NOT weaken security controls merely to make scanning easier.

Do NOT:

* mount the Docker socket into an untrusted/floating external container;
* use `latest` scanner images;
* disable vulnerability severity checks;
* suppress findings without evidence.

Prefer, in order:

1. an existing repository CI vulnerability-scanning job operating against the exact production images;
2. an already-installed trusted local scanner;
3. a pinned scanner binary/tool installed using the repository's accepted tooling mechanism;
4. exporting/saving the final Docker image and scanning the resulting artifact if direct image access is constrained.

If hosted CI already performs a trustworthy HIGH/CRITICAL scan of the exact final production images, that evidence may satisfy this gate. Document exactly which workflow/job performs the scan and what was scanned.

Required acceptance:

* zero unresolved HIGH vulnerabilities;
* zero unresolved CRITICAL vulnerabilities.

For any reported finding:

* determine whether it is present in the shipped runtime;
* remediate when applicable;
* rebuild;
* rescan.

Do not dismiss findings without documented evidence.

---

## 6. VERIFY IMAGE/COMMIT CONSISTENCY

Make sure the images being accepted correspond to the final source commit.

If committing changes modifies anything that affects either production image, rebuild the affected image and update its digest before acceptance.

Do not claim the previously recorded image digest represents the final commit if image-affecting files changed afterward.

---

## 7. UPDATE PHASE 1 RESULTS

Update:

`docs/phase-1-results.md`

Include the final:

* branch
* commit SHA
* API image digest
* Web image digest
* vulnerability-scan command/method
* scan results
* hosted CI run/result
* final validation results
* known limitations, if any

Clearly distinguish:

* implementation complete
* candidate commit created
* release gates passed
* Phase 1 accepted

Only state that Phase 1 is release-ready if all required gates are green.

---

## 8. IF DOCUMENTATION CHANGES AFTER THE CANDIDATE COMMIT

If `docs/phase-1-results.md` must be updated after hosted CI or vulnerability scanning:

1. update the document;
2. commit the documentation change;
3. push it.

If the documentation-only commit does not affect application/runtime/container inputs, do not unnecessarily rebuild production images.

However, hosted CI for the final pushed commit must still be reviewed as required by the repository's workflow.

---

## 9. FINAL RESPONSE

Report:

* Phase 1 acceptance status
* branch
* final commit SHA
* commit message(s)
* push result
* API image digest
* Web image digest
* vulnerability scan result
* hosted CI result
* any remaining blocker
* whether Phase 1 is ready for release acceptance

Do NOT begin Phase 2.

Stop after Phase 1 release-gate verification.
