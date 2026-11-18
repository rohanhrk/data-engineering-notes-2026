---

## 6. Interview Preparation — Questions WITH Answers

### A. Conceptual Questions (10)

**Q1. What is IAM and what are its main building blocks?**
IAM is AWS's service for controlling authentication (who you are) and authorization (what you may do). Building blocks: **users** (long-term identities), **groups** (sets of users), **roles** (assumable identities with temporary credentials), **policies** (JSON permissions), and **STS** (issues temporary credentials). Every API call is evaluated against policies; the default is deny. *Keywords: principal, policy, role, least privilege, implicit deny.* It is global, free, and the base of all pipeline security — e.g. Glue, Lambda and EMR each use roles.

**Q2. Difference between an IAM user, group and role?**
A **user** represents a person or app with long-term credentials (password/access keys). A **group** is only a container of users for attaching policies — it cannot be assumed and cannot be a principal in policies. A **role** has no permanent credentials; a trusted principal (service, user, account, federated identity) *assumes* it and gets temporary credentials. Roles are preferred for services and cross-account access because there is nothing to leak or rotate manually. Example: Lambda uses an execution role, a human uses SSO to assume `DataEngineerRole`.

**Q3. Explain identity-based vs resource-based policies.**
Identity-based policies attach to a user/group/role and define what that identity can do. Resource-based policies attach to a resource (S3 bucket, SQS queue, KMS key, Lambda function, role trust policy) and include a **Principal** element defining who can access the resource. Within one account, either type allowing the action is enough. For cross-account access both the caller's identity policy and the resource policy must allow (unless the caller assumes a role in the resource's account). Example: an S3 bucket policy allows another account's role to read objects.

**Q4. What is the difference between a trust policy and a permission policy?**
A role has two separate kinds of policy. The **trust policy** (assume-role policy) says *who is allowed to assume the role* (e.g. `glue.amazonaws.com`, another account, an OIDC provider). The **permission policy** says *what the role can do* after it is assumed. A frequent bug: permissions are perfect but the service cannot assume the role because the trust policy names the wrong service principal. Remember: trust = door; permissions = what is inside the room.

**Q5. How does IAM evaluate permissions? What overrides what?**
Start from **implicit deny**. If any applicable policy has an **explicit Deny**, the request is denied regardless of Allows. Organisation SCPs, permission boundaries and session policies must also allow the action (they set maximum permissions). Finally there must be an **Allow** in an identity-based and/or resource-based policy. So: explicit deny > (guardrails must allow) > allow > implicit deny. Practical use: an SCP denying regions or a bucket policy denying non-TLS traffic cannot be bypassed by a broad Allow.

**Q6. What is STS and how does `AssumeRole` work?**
Security Token Service issues short-lived credentials. A principal calls `AssumeRole` with a role ARN; IAM checks that the role's trust policy trusts the caller (and the caller is permitted to call `sts:AssumeRole` if in another account/or via identity policy); STS returns an access key, secret key and **session token** valid for a duration (e.g. 1 hour). The caller uses them for subsequent calls. Benefits: no long-term secrets, automatic expiry, session names for auditing in CloudTrail, optional MFA and ExternalId conditions.

**Q7. How do you grant cross-account access?**
Two common ways. (1) **Role-based:** Account B creates a role trusting Account A's principal; Account A allows its users to `sts:AssumeRole` on that role; users assume it and act inside Account B. (2) **Resource-based:** Account B's resource policy (e.g. an S3 bucket policy) names Account A's principal; Account A's identity policy also allows the action. Remember encryption: with SSE-KMS the key policy/grant must allow the other account's role. Use `ExternalId` for third parties and `aws:PrincipalOrgID` to limit to your organisation.

**Q8. What is least privilege and how would you implement it for a pipeline?**
Least privilege means giving only the permissions needed, on the narrowest resources, for the shortest time. For a Glue job: a dedicated role; `s3:GetObject` on the input prefix, `s3:PutObject` on the output prefix, `s3:ListBucket` with a prefix condition, `glue:GetTable/GetPartitions` for specific databases, `logs:*` for its log group only, and `kms:Decrypt/GenerateDataKey` for the key used. Start restrictive, test, expand when `AccessDenied` shows a real need. Use IAM Access Analyzer's policy generation from CloudTrail and "last accessed" data to prune later.

**Q9. What is `iam:PassRole` and why is it required?**
When you configure a service to act with a role (e.g. create a Glue job with `GlueEtlRole`, a Lambda with an execution role, an EMR cluster with a service role), your identity must have `iam:PassRole` on that role. This prevents users from escalating privileges by attaching a more powerful role to a service they control. You can limit it with the condition `iam:PassedToService`. Missing PassRole is a very common error when deploying pipelines with Terraform/CloudFormation/CI.

**Q10. Why use roles and IAM Identity Center instead of long-term access keys? What are best practices for credentials?**
Long-term keys can be leaked in code, logs or laptops and rarely get rotated. Roles/SSO give temporary credentials that expire, support MFA, are centrally managed and audited. Best practices: lock away root with MFA; no root access keys; use SSO for humans; roles for workloads (instance/task/execution roles, OIDC for CI/CD); if keys are unavoidable, rotate them, store in Secrets Manager, and monitor via credential report and CloudTrail. Enable MFA, and use Access Analyzer to detect unintended external access.

### B. Scenario-Based Questions (5)

**S1. A Glue job fails with `AccessDenied` reading S3 even though "the role has S3 access".**
*Scenario:* the role policy lists `s3:GetObject` on `arn:aws:s3:::lake`. *Problem:* object actions need object ARNs (`lake/*`), and `s3:ListBucket` needs the bucket ARN. *Solution:* separate statements: ListBucket on `arn:aws:s3:::lake` (with optional `s3:prefix` condition) and GetObject on `arn:aws:s3:::lake/raw/*`; check KMS decrypt and bucket policy denies. *Why:* S3 evaluates action against the specific resource type. *Alternatives:* attach the AWS managed `AmazonS3ReadOnlyAccess` (too broad for production). *Trade-off:* precise policies take more care but are safer.

**S2. A partner's AWS account must read one curated dataset in your lake.**
*Solution:* create a role `PartnerReadCurated` in your account with permission to `s3:GetObject` on only that prefix; trust policy naming the partner account (with `sts:ExternalId` condition); partner users get `sts:AssumeRole` permission in their account; if objects use SSE-KMS add the role to the key policy. Optionally use a bucket policy/Access Point or Lake Formation cross-account sharing for table-level control. *Why:* no shared credentials, revocable by editing the trust policy. *Alternatives:* S3 bucket policy directly granting the partner role; pre-signed URLs for ad hoc sharing. *Trade-off:* Lake Formation adds governance but extra setup.

**S3. Your CI/CD pipeline uses an IAM user's access keys stored as GitHub secrets. Security wants them removed.**
*Solution:* configure GitHub as an **OIDC identity provider** in IAM and create a role whose trust policy allows `sts:AssumeRoleWithWebIdentity` from that provider, restricted by conditions on repository and branch (`token.actions.githubusercontent.com:sub`). The workflow assumes the role at runtime and gets temporary credentials; delete the old keys. *Why:* no long-lived secrets; scoped to repo/branch. *Alternatives:* self-hosted runners with instance roles; Identity Center for humans. *Trade-off:* initial setup effort, need careful condition on `sub` to avoid any repo assuming the role.

**S4. Developers must create roles for their own Glue jobs but must not become admins.**
*Solution:* use **permissions boundaries**: allow developers `iam:CreateRole` and `iam:AttachRolePolicy` only when the created role has the boundary policy attached (condition `iam:PermissionsBoundary`), and restrict `iam:PassRole` to those roles. The boundary caps what any created role can do (e.g. S3/Glue only). *Why:* delegation without privilege escalation. *Alternatives:* centralised platform team creates roles via IaC; SCPs for organisation-level guardrails. *Trade-off:* boundaries are complex to author and debug.

**S5. An analyst can see a Glue table in the console but Athena returns permission errors on the underlying data.**
*Explanation:* seeing metadata requires Glue permissions; reading data requires S3 (and KMS) permissions — or, if Lake Formation governs the table, Lake Formation grants. *Solution:* verify the analyst role's S3 read permission on the table location and KMS key; if Lake Formation is enabled, grant `SELECT` on the table/columns and ensure the S3 location is registered. Use CloudTrail to identify the denied action and principal. *Alternatives:* manage with IAM only (simple) or Lake Formation (fine-grained). *Trade-off:* Lake Formation gives column/row-level security but adds a second permission layer.

### C. Troubleshooting Questions (3)

**T1. "User is not authorized to perform: sts:AssumeRole on resource role/X".**
*Possible root causes:* the role's trust policy does not list the caller (wrong account/role ARN); the caller's identity policy lacks `sts:AssumeRole`; a condition (MFA, ExternalId, source IP) is not satisfied; the caller is itself an assumed-role session and the trust policy names the underlying role ARN incorrectly; SCP blocks STS. *Debug:* `aws sts get-caller-identity` to see the true caller ARN; `aws iam get-role --role-name X` to read the trust policy; compare principal ARNs; check conditions and SCPs; try the policy simulator. *Fix:* update the trust policy principal and/or add `sts:AssumeRole` permission for the caller; supply `--external-id` or MFA token if required. Wait a few seconds for IAM propagation.

**T2. Glue job creation fails with "not authorized to perform iam:PassRole".**
*Root causes:* the identity creating the job has no `iam:PassRole` for the role ARN; condition `iam:PassedToService` doesn't match; the role is in another account/path. *Debug:* read the error ARN; check the identity's policies with `aws iam list-attached-user-policies` / `list-attached-role-policies`; use `simulate-principal-policy` for `iam:PassRole`. *Fix:*
```json
{"Effect":"Allow","Action":"iam:PassRole",
 "Resource":"arn:aws:iam::111122223333:role/GlueEtlRole",
 "Condition":{"StringEquals":{"iam:PassedToService":"glue.amazonaws.com"}}}
```

**T3. An S3 object read fails with `AccessDenied` although IAM and bucket policy allow it.**
*Root causes:* explicit Deny in a bucket policy or SCP (e.g. requires VPC endpoint or TLS); the object is encrypted with SSE-KMS and the role lacks `kms:Decrypt` or the key policy doesn't trust the role; permissions boundary or session policy limits access; S3 Block Public Access/Access Point policy; cross-account missing one side; Lake Formation governs the location. *Debug approach:* (1) `aws sts get-caller-identity`; (2) `aws s3api head-object` to see encryption; (3) check bucket policy `Deny` statements and SCPs; (4) policy simulator with the real principal; (5) CloudTrail event shows `errorMessage` mentioning explicit deny or KMS. *Fix:* adjust the offending layer — e.g. add the role to the KMS key policy, satisfy the condition (use the VPC endpoint), or remove the explicit deny.

---

## 7. Revision and Quick Reference

### Key takeaways
- Everything in AWS is authorized by IAM; default is deny; explicit deny wins.
- Roles + temporary credentials > users + access keys.
- Two policies on a role: trust (who) and permissions (what).
- Use least privilege, MFA, SSO, and audit with CloudTrail/Access Analyzer.

### Commonly forgotten details
- `iam:PassRole` is required to attach a role to a service.
- Groups can't be assumed or used as principals.
- Cross-account needs both sides to allow (or role assumption).
- SCPs/boundaries restrict but never grant.
- S3 `ListBucket` uses the bucket ARN; object actions use `bucket/*`.
- KMS needs its own permission (key policy + IAM/grant).
- JSON policies cannot contain comments.
- IAM is eventually consistent — changes may take seconds.

### Important commands
```bash
aws sts get-caller-identity
aws iam create-role --role-name R --assume-role-policy-document file://trust.json
aws iam put-role-policy --role-name R --policy-name P --policy-document file://perm.json
aws iam attach-role-policy --role-name R --policy-arn <arn>
aws iam list-roles ; aws iam get-role --role-name R
aws sts assume-role --role-arn <arn> --role-session-name test
aws iam simulate-principal-policy --policy-source-arn <arn> --action-names s3:GetObject --resource-arns <arn>
aws iam generate-credential-report ; aws iam get-credential-report
```

### Frequently used configurations
Service principals: `glue.amazonaws.com`, `lambda.amazonaws.com`, `elasticmapreduce.amazonaws.com`, `ec2.amazonaws.com`, `redshift.amazonaws.com`, `firehose.amazonaws.com`, `states.amazonaws.com`. Managed policies: `AWSGlueServiceRole`, `AWSLambdaBasicExecutionRole`, `AWSLambdaKinesisExecutionRole`, `AmazonS3ReadOnlyAccess` (broad — avoid in production).

### Common errors and solutions
| Error | Solution |
|---|---|
| AccessDenied | Find denying layer: identity policy, resource policy, SCP, boundary, KMS, Lake Formation |
| `sts:AssumeRole` not authorized | Fix trust policy and caller permission |
| `iam:PassRole` not authorized | Add PassRole for that role ARN |
| ExpiredToken | Refresh credentials; check session duration |
| MalformedPolicyDocument | Validate JSON, ARNs, remove comments |

### Service limitations
Policy size limits apply (inline/managed policy character limits and quotas on attached policies per role/user — check IAM quotas); role session duration limited (role chaining max 1 hour); IAM is global and eventually consistent; roles per account have quotas that can be raised.

### Performance and cost optimisation
IAM is free. Avoid excessive STS calls by caching credentials (SDKs do); reduce KMS call volume with S3 Bucket Keys; use IaC to avoid manual drift.

### Security best practices
MFA everywhere; no root keys; SSO for people; roles for workloads; least privilege; permission boundaries and SCPs; Access Analyzer; CloudTrail enabled org-wide; rotate/disable unused keys; use conditions (`aws:PrincipalOrgID`, `aws:SourceArn`).

### Connections with other AWS services
S3 (bucket policies), KMS (key policies), Glue/EMR/Lambda/Redshift (service roles), Lake Formation (data permissions), Organizations (SCPs), CloudTrail (audit), Secrets Manager (credentials), IAM Identity Center (SSO), CloudFormation/Terraform (IaC).

### Quick revision cheat sheet
```
Deny (explicit) > SCP/boundary/session must allow > Allow > implicit deny
Role = trust policy (WHO assumes) + permission policy (WHAT it can do)
STS AssumeRole -> temp creds (key+secret+token)
PassRole to attach a role to a service
Cross-account: trust + permission (or bucket policy + identity policy)
S3: ListBucket -> bucket ARN, Get/Put -> bucket/*
```

### 10 rapid-fire revision questions
1. **Default decision when no policy matches?** Implicit deny.
2. **What beats an Allow?** An explicit Deny.
3. **Can a group be a principal or be assumed?** No.
4. **Which policy defines who can assume a role?** The trust (assume-role) policy.
5. **What does STS return?** Access key ID, secret key and session token with expiry.
6. **Why `iam:PassRole`?** Stops privilege escalation when attaching roles to services.
7. **Do SCPs grant permissions?** No — they only limit.
8. **How should humans access AWS in multi-account setups?** IAM Identity Center/SSO.
9. **What is ExternalId for?** Prevents the confused deputy problem with third parties.
10. **Tool to generate least-privilege policies from usage?** IAM Access Analyzer policy generation.

---

## Official AWS documentation
- IAM User Guide — https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html
- Policy evaluation logic — https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html
- IAM roles — https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html
- Temporary credentials / STS — https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html
- Cross-account access — https://docs.aws.amazon.com/IAM/latest/UserGuide/tutorial_cross-account-with-roles.html
- Best practices — https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- Permissions boundaries — https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html
- IAM Access Analyzer — https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html
- Boto3 IAM/STS reference — https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html
