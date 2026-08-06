---
title: Aws Cdk Typescript
trigger: project contains cdk.json, or a package.json depending on aws-cdk-lib or
  aws-cdk
---
- Run `npx cdk diff` and read the change set before every `npx cdk deploy`; never deploy an unreviewed diff.
- Keep one stack per deployable unit and pass environment in as a stack prop; do not branch on `process.env` inside constructs.
- Never mutate deployed infrastructure from the console or AWS CLI; change the CDK source and redeploy so the template stays authoritative.
- Commit `cdk.json` but never `cdk.out/`; synthesized templates are build output.
- Grant least privilege through the generated `grant*` helpers rather than hand-written wildcard IAM statements.
