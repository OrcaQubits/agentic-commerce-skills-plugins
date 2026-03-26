---
name: sf-setup
description: Set up a Salesforce Commerce development environment — sfcc-ci CLI for B2C, sf CLI for B2B, Business Manager access, sandbox management, dw.json configuration, .sfdx project setup, and project structures for SFRA, PWA Kit, and Lightning. Use when starting a new Salesforce Commerce project.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Salesforce Commerce Development Setup

## Before Writing Code

**Fetch live docs before setting up a project.**

1. Web-fetch: `https://github.com/SalesforceCommerceCloud/sfcc-ci` for sfcc-ci CLI commands
2. Web-search: "site:developer.salesforce.com sf cli getting started 2026" for sf CLI setup
3. Web-search: "site:developer.salesforce.com SFRA getting started 2026" for SFRA project setup
4. Web-fetch: `https://github.com/SalesforceCommerceCloud/storefront-reference-architecture` for SFRA reference
5. Web-search: "site:developer.salesforce.com commerce cloud b2c b2b documentation 2026"

## Conceptual Architecture

### Prerequisites

**B2C Commerce (SFCC) requires:**
- Business Manager account (provided by Salesforce or your org)
- Sandbox instance (e.g., `dev01-realm-customer.demandware.net`)
- API client credentials (client ID + secret) for sfcc-ci authentication
- Account Manager credentials for WebDAV/OCAPI

**B2B Commerce (Lightning) requires:**
- Salesforce org (Developer Edition, sandbox, or production) with B2B Commerce license
- sf CLI installed (`npm install -g @salesforce/cli`)
- Scratch org or sandbox for isolated development

### CLI Tools

| Tool | Platform | Install | Auth |
|---|---|---|---|
| sfcc-ci | B2C | `npm install -g sfcc-ci` | `sfcc-ci client:auth` (client ID + secret) |
| sf CLI | B2B | `npm install -g @salesforce/cli` | `sf org login web` or `sf org login jwt` |

**Key sfcc-ci Commands:**
- `sfcc-ci code:deploy` -- upload code to sandbox
- `sfcc-ci code:activate` -- activate a code version
- `sfcc-ci sandbox:create` / `sandbox:list` -- manage on-demand sandboxes
- `sfcc-ci job:run` -- execute Business Manager jobs

**Key sf CLI Commands:**
- `sf project deploy start` -- deploy metadata to org
- `sf org create scratch` -- create scratch org
- `sf apex run test` -- run Apex tests
- `sf data import tree` -- import sample data

### Project Structures

**B2C SFRA Cartridge Project:**

```
sfra-project/
  cartridges/
    app_storefront_base/       # Base (never modify)
    app_custom_storefront/     # Custom overlay
      cartridge/
        controllers/, models/, scripts/
        templates/, client/ (js, scss)
  dw.json, package.json, webpack.config.js
```

**B2C PWA Kit Project:**

```
pwa-kit-project/
  app/
    components/, pages/, hooks/, utils/
    commerce-api/              # Commerce Cloud API client
  config/
    default.js, production.js
  package.json, .env
```

**B2B Lightning Project:**

```
b2b-lightning-project/
  force-app/main/default/
    lwc/, classes/, triggers/
    objects/, flexipages/
    experiences/, permissionsets/
  config/project-scratch-def.json
  sfdx-project.json, .forceignore
```

### Configuration Files

**dw.json (B2C):**
- Placed in project root; configures hostname, code-version, cartridge list, excludes
- **Never commit with credentials** -- use environment variables or `.env` excluded from VCS

**sfdx-project.json (B2B):**
- Placed in project root; defines packageDirectories, sourceApiVersion, namespace, login URL

**.forceignore (B2B):**
- Excludes files from deployment (jsconfig.json, .eslintrc.json, logs, OS files)

### Key Configuration Fields

**B2C dw.json fields:**
- `hostname` -- sandbox domain
- `username` / `password` -- credentials (prefer env vars)
- `code-version` -- target code version
- `cartridges` -- array of cartridge names to upload
- `exclude` -- files/directories to skip

**B2B sfdx-project.json fields:**
- `packageDirectories` -- array of source paths (typically `force-app`)
- `sourceApiVersion` -- Salesforce API version (e.g., `"61.0"`)
- `namespace` -- package namespace (empty for unmanaged)
- `sfdcLoginUrl` -- org login URL

### Sandbox and Org Types

| Type | Platform | Purpose |
|---|---|---|
| Development sandbox | B2C | Developer-specific feature work |
| Staging sandbox | B2C | Pre-production validation |
| On-demand sandbox | B2C | Temporary, via `sfcc-ci sandbox:create` |
| Scratch org | B2B | Short-lived, disposable dev org |
| Developer sandbox | B2B | Partial copy of production |
| Full sandbox | B2B | Full copy of production for UAT |

### Environment Variables

Store credentials as environment variables, never in committed files.

**B2C:** `SFCC_CLIENT_ID`, `SFCC_CLIENT_SECRET`, `SFCC_HOSTNAME`, `SFCC_USERNAME`, `SFCC_PASSWORD`, `SFCC_CODE_VERSION`

**B2B:** `SF_USERNAME`, `SF_ORG_ALIAS`, `SF_CLIENT_ID`, `SF_JWT_KEY_FILE` (for CI/CD connected app auth)

### Deprecated Technologies

| Deprecated | Replacement |
|---|---|
| dwupload | sfcc-ci |
| sfdx CLI (old) | sf CLI (unified) |
| Prophet Debugger | Official Salesforce VS Code extensions |

## Best Practices

### B2C Commerce
- Use `sfcc-ci` for all deployments; never use manual WebDAV upload
- Never modify `app_storefront_base` directly; always overlay in custom cartridge
- Build assets (`npm run compile:js`, `npm run compile:scss`) before deployment
- Keep `dw.json` out of version control (add to `.gitignore`)

### B2B Commerce
- Use `sf project deploy start` for metadata deployment; avoid Change Sets
- Create scratch orgs for feature development; keep them isolated
- Use source tracking (`sf project deploy preview`) to review changes before deploy
- Use Permission Sets for access control; avoid modifying profiles directly

### Both Platforms
- Use environment variables for all secrets and instance-specific configuration
- Set up CI/CD pipelines for automated testing and deployment
- Use linting (ESLint, Prettier for JS; Apex PMD for Apex)

Fetch the sfcc-ci documentation, SFRA getting-started guide, and sf CLI reference for exact commands and latest project structures before setting up.
