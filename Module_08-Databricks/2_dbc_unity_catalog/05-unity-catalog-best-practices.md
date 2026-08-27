# Unity Catalog Best Practices

## 1. Identity Management

Use account-level identities.

Recommended pattern:

```mermaid
flowchart LR
    IDP[Identity Provider] --> AG[Account Groups]
    AG --> UC[Unity Catalog]
    UC --> DATA[Data Assets]
```

Prefer:

- Identity provider integration
- Automatic identity management where supported
- SCIM when required
- Groups instead of direct user grants

Avoid manually managing users everywhere.

## 2. Group-Based Access

Bad:

```text
Table
 |
 +-- User A
 +-- User B
 +-- User C
 +-- User D
```

Better:

```text
Table
 |
 +-- data-analysts
       |
       +-- User A
       +-- User B
       +-- User C
       +-- User D
```

Benefits:

- Easier onboarding
- Easier offboarding
- Centralized authorization
- Less privilege sprawl

## 3. Production Ownership

Assign production ownership to groups.

```text
prod_catalog
     |
     v
data-platform-admins
```

rather than:

```text
prod_catalog
     |
     v
individual-user
```

This avoids a production governance dependency on one person.

## 4. Service Principals for Production Jobs

Prefer:

```text
Service Principal
       |
       v
Production Job
       |
       v
Production Table
```

instead of:

```text
Personal User
       |
       v
Production Job
```

This makes automation more stable and reduces accidental production changes.

## 5. Catalog Design

Catalogs are the primary data-isolation layer in the typical Unity Catalog model.

Possible designs:

```text
prod
├── finance
├── sales
└── hr
```

or:

```text
finance
├── bronze
├── silver
└── gold
```

or another design aligned with:

- Business units
- Environment
- Teams
- Regulatory boundaries
- Workspace isolation

Do not create catalogs simply because a new table exists.

## 6. Schema Design

Schemas provide a second organizational/access-control layer.

Example:

```text
sales
├── bronze
├── silver
└── gold
```

A common team-oriented approach is to create schemas that correspond to team responsibilities.

## 7. Use BROWSE for Discoverability

A modern governance model should not mean:

> Hide everything from everyone.

Instead:

```text
Discover metadata
       |
       v
Request access
       |
       v
Approved access
```

`BROWSE` can support discovery without granting data access.

## 8. Least Privilege

Start with:

```text
No access
    |
    v
Required usage privileges
    |
    v
Required data privilege
```

Example:

```sql
GRANT USE CATALOG
ON CATALOG sales
TO `sales-analysts`;

GRANT USE SCHEMA
ON SCHEMA sales.analytics
TO `sales-analysts`;

GRANT SELECT
ON TABLE sales.analytics.orders
TO `sales-analysts`;
```

## 9. Avoid Broad ALL PRIVILEGES

Use:

```text
SELECT
MODIFY
CREATE TABLE
USE CATALOG
USE SCHEMA
```

where appropriate instead of automatically using:

```text
ALL PRIVILEGES
```

Broad privileges should be reserved for trusted administrative roles.

## 10. Managed Tables for Most New Tables

Current Databricks guidance recommends managed tables for most use cases and for new tables.

Use external tables when there is a clear reason, such as:

- Existing data
- Migration
- External access requirements
- Specific DR needs
- Unsupported format requirements

## 11. Protect Cloud Storage

Avoid:

```text
User ---> Direct S3 Access
```

when the data is intended to be governed by Unity Catalog.

Prefer:

```text
User
 |
 v
Unity Catalog
 |
 +--> Table / Volume / External Location
 |
 v
S3
```

This preserves governance and auditability.

## 12. External Locations

External locations can represent broad paths.

Therefore:

> Give `CREATE EXTERNAL LOCATION` only to administrators or trusted data engineers who are responsible for configuring cloud-storage integration.

For end users, prefer more granular access through tables and volumes.

## 13. External Location per Schema

For external data organization, Databricks recommends creating external tables/volumes using an external location pattern that provides appropriate granularity, with one external location per schema being a recommended practice for external tables/volumes.

## 14. Avoid Registering the Same External Table in Multiple Metastores

Do not repeatedly register the same frequently accessed external table across multiple metastores.

This can create metadata consistency problems.

For sharing data between metastores, use supported sharing mechanisms such as OpenSharing where appropriate.

## 15. Workspace Isolation

Use workspace-catalog binding when you need strong environment isolation.

Example:

```text
Production Catalog
       |
       +--> Production Workspace

Development Catalog
       |
       +--> Development Workspace
```

This helps prevent accidental access to production data from development environments.

## 16. Managed Storage

Prefer catalog-level managed storage as the primary data-isolation unit where appropriate.

Avoid allowing external systems/users to bypass Unity Catalog and directly access managed-storage buckets.

## 17. Views for Controlled Access

Views can expose only the data required by a user/group.

Concept:

```text
Base Table
   |
   +--> Secure View
            |
            v
        Analysts
```

This can be useful for:

- Column restriction
- Row filtering
- Business-specific data products

## 18. Production MODIFY Access

Reserve direct `MODIFY` access on production tables for trusted service principals or tightly controlled engineering groups.

Typical pattern:

```text
Analyst
  |
  +--> SELECT

ETL Service Principal
  |
  +--> MODIFY
```

## 19. Governance Checklist

```text
Identity
  -> Account-level users/groups
  -> IdP integration

Access
  -> Group-based grants
  -> Least privilege
  -> USE CATALOG
  -> USE SCHEMA
  -> SELECT/MODIFY only where required

Storage
  -> Managed tables by default
  -> External locations for controlled external storage
  -> Avoid direct S3 bypass

Isolation
  -> Catalog boundaries
  -> Workspace-catalog bindings

Operations
  -> Service principals
  -> Audit logs
  -> Lineage
  -> Data classification
  -> Regular access review
```

## 20. Golden Rules

Remember these:

1. **Catalog is the primary data-isolation unit.**
2. **Schema provides another organization/access layer.**
3. **Use groups instead of direct user grants.**
4. **Use service principals for production automation.**
5. **Use managed tables for most new tables.**
6. **Do not bypass Unity Catalog with direct cloud-storage access.**
7. **Use least privilege.**
8. **Use `BROWSE` for discoverability without data access.**
9. **Use workspace-catalog binding for workspace isolation.**
10. **Use lineage and audit information for governance and troubleshooting.**
11. **Be careful with powerful privileges such as `MANAGE` and `ALL PRIVILEGES`.**
12. **Treat external locations as sensitive because they can represent broad cloud-storage paths.**

## Official references

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/best-practices
- https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/
- https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/privileges-reference
