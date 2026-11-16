# Part 2 — Approximate AWS costs

**Planning estimate, not an AWS bill or a capacity benchmark.**
For the assumptions below, allow roughly **$1,100–$1,400/month** with a
Single-AZ database, or **$2,000–$2,400/month** with one Multi-AZ standby.
The upper figures include about 20% contingency, not a statistical confidence
interval. Larger text, heavier queries or more database capacity can exceed them.

## Price date and scope

Prices were checked on **2026-11-16**, in USD, for **US East (N. Virginia),
`us-east-1`**, using official AWS sources. This region is a budgeting example,
not an approved deployment location; the diagram deliberately leaves it TBD.

The selected ECS, RDS and S3 catalog rates are effective **November 1, 2026**.
Catalog publication dates and SKUs are listed below. Page consultation dates
are not publication dates.

Use 730 hours/month and On-Demand prices. No Free Tier credits, Savings Plans,
Reserved Instances, Spot discounts or tax deductions are assumed. Taxes,
paid support and engineering time are outside this estimate.

## Assumptions we can change

These quantities are budget inputs, not measurements from Part 1:

| Input | Budget assumption |
|---|---|
| Corpus | 10 million patents, averaging 100 KiB of source JSON each |
| Source storage | About 954 GiB of JSON, rounded to 1,024 GiB in S3 Standard |
| Database storage | 3,072 GiB gp3 for rows, retained source content, passages, vectors, indexes and headroom |
| Database compute | One `db.m7g.2xlarge`: 8 vCPU / 32 GiB, Single-AZ in the baseline |
| API | Two Linux/x86 tasks, each 1 vCPU / 2 GiB, running all month across two AZs |
| Search traffic | 100,000 requests/month, with short peaks around 5 requests/second |
| Responses | Around 20 KiB each; no bulk downloads through the API |
| Freshness | Weekly batch updates; 120 total ingestion task-hours/month at 2 vCPU / 4 GiB |
| Backups | Seven-day automated retention; budget 500 GiB beyond the included backup allowance |
| Private connectivity | Four interface endpoints in each of two AZs; S3 Gateway Endpoint; no NAT |
| Observability | Around 10 GiB of logs/month, 30-day log retention and a small alarm budget |
| Availability | Two API tasks; database Single-AZ unless choosing the standby scenario below |

There is no measured relationship yet between this instance size, the workload
and a response-time target. In particular, 32 GiB RAM will not cache a 3 TiB
database. The first sizing exercise must measure query plans, working set,
storage/GIN growth, counting, evidence selection and ingestion contention.
The 3 TiB allocation is a sizing assumption, not a proven storage requirement.
For comparison, the supplied JSON sample averages about 24.3 KiB per patent
(15,939,070 bytes / 640); it does not establish the full corpus's average or
the size of normalized rows and indexes.

## Monthly baseline

Amounts are rounded; the formulas explain how to replace the assumptions.

| Component | Calculation / allowance | Approx. USD/month |
|---|---|---:|
| Fargate API | `2 × 730 × (1 × 0.04048 + 2 × 0.004445)` | 72 |
| Fargate ingestion | `120 × (2 × 0.04048 + 4 × 0.004445)` | 12 |
| RDS compute | `730 × 0.674` | 492 |
| RDS gp3 storage | `3,072 × 0.115` | 353 |
| Extra RDS backup storage | `500 × 0.095` | 48 |
| S3 Standard storage | `1,024 × 0.023` | 24 |
| S3 requests | 10,000 PUT/LIST and 100,000 GET at $0.005/$0.0004 per 1,000 | <1 |
| Application Load Balancer | `730 × (0.0225 + 1 × 0.008)`; budget one average LCU | 22 |
| Public IPv4 for ALB | Two addresses: `2 × 730 × 0.005` | 7 |
| Interface endpoints | `4 services × 2 AZs × 730 × 0.01` | 58 |
| Endpoint data processing | 50 GB at $0.01/GB | <1 |
| CloudWatch | Allowance for log ingestion/storage and a few alarms | 10 |
| ECR | 5 GB of private image storage at $0.10/GB-month | 1 |
| Secrets Manager | Two secrets at $0.40/month + 20,000 API calls at $0.05/10,000 | 1 |
| Other network transfer | Allowance for cross-AZ traffic and shared internet-egress usage | 20 |
| **Estimated baseline** | Unrounded calculations total about $1,120 | **1,120** |
| **With 20% contingency** | Rounded planning budget | **1,350** |

Fargate rates are per vCPU-hour and memory GiB-hour. Its included 20 GiB of
ephemeral storage per task is assumed sufficient for bounded streaming/batches;
larger scratch volumes cost extra. RDS storage is provisioned capacity, not only
used bytes. No additional gp3 IOPS/throughput are provisioned in this estimate.

The ALB LCU is a usage allowance, not a compulsory minimum; actual billing uses
the highest of its connection, byte and rule-evaluation dimensions. Its IPv4
count may grow with the load balancer. The transfer allowance is not a flat AWS
tariff: AWS's shared 100 GB/month internet-egress allowance might already be used
elsewhere in the account. Reprice actual transfer volumes before deployment.

IAM roles, VPC/subnets/security groups, the S3 Gateway Endpoint and a standard
non-exportable ACM public certificate for the ALB have no separate service charge
in this model. DNS/domain registration, customer-managed KMS keys, CloudTrail
trails, WAF, enhanced database monitoring and paid support are not included.
The model assumes no customer-managed KMS keys and no private certificate CA.

## Availability and growth

**Multi-AZ database with one standby:** replace the database rate with
$1.348/hour and the storage rate with $0.23/GiB-month. Those are the combined
Multi-AZ rates; do not multiply by two again. This adds about **$845/month**,
bringing the same system to **$1,966/month**, or roughly **$2,360 with contingency**.
This standby provides failover, not extra query-serving capacity. It is not the
three-instance Multi-AZ DB cluster product.

Some useful sensitivities:

- Each additional always-running 1 vCPU / 2 GiB API task costs about **$36/month**.
  An autoscaling maximum is not a fixed bill: charge for actual extra task-hours.
- Each additional 1 TiB of RDS storage costs about **$118/month Single-AZ** or
  **$236/month Multi-AZ**, before extra backups.
- Doubling the chosen database compute adds about **$492/month Single-AZ**.
  This is a budget sensitivity, not a promise of twice the throughput.
- Keeping more source versions, rebuilding indexes or restoring a second database
  can temporarily require much more storage than steady-state operation.

The baseline uses endpoints for `ecr.api`, `ecr.dkr`, `secretsmanager` and `logs`
in both AZs, plus the free S3 Gateway Endpoint for source objects and image layers.
Built-in service metrics do not require the containers to call a custom metrics
endpoint. If they publish custom metrics, add its connectivity and usage costs.

As an alternative, two NAT Gateways at $0.045/hour plus two public IPv4 addresses
would cost about **$73/month before $0.045/GB processing**. This would replace,
not automatically add to, the endpoint design. One NAT would be cheaper but
introduce an AZ dependency and possible cross-AZ charges. Keep the S3 Gateway
Endpoint either way. Neither option is universally cheaper.

## Initial ingestion is a separate variable

We have not measured ingestion throughput on this AWS setup. Do not extrapolate
the sample's import time into a completion date for ten million patents.

For illustration, a Linux/x86 worker with **4 vCPU / 16 GiB** costs:

```text
hourly worker cost = 4 × $0.04048 + 16 × $0.004445 = $0.23304
100–1,000 aggregate worker-hours = about $23–$233 of worker compute
```

That is a sensitivity range, not a prediction of required hours or the full
initial-load bill. Add the database/storage costs during the loading period,
source requests, logs, temporary storage and any temporary database upgrade.
If loading happens within an already-budgeted month, do not count that month's
unchanged database cost twice. Multiple workers may shorten elapsed time only
until database write/index contention becomes the bottleneck.

## Official sources and rate evidence

All consulted on **2026-11-16**. The audit independently rechecked the selected
ECS, RDS and S3 catalog rates and cost arithmetic. Catalog responses are not
archived here; URLs ending in `current` can change, so these links do not
reproduce a historical price quote.

| Source | Rates / rules used |
|---|---|
| [Fargate pricing](https://aws.amazon.com/fargate/pricing/) and [ECS regional catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonECS/current/us-east-1/index.json) | Published Nov 11; SKUs `8CESGAFWKAJ98PME` ($0.04048/vCPU-hour), `PBZNQUSEXZUC34C9` ($0.004445/GB-hour); effective Nov 1 |
| [RDS PostgreSQL pricing](https://aws.amazon.com/rds/postgresql/pricing/) and [RDS regional catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonRDS/current/us-east-1/index.json) | Published Nov 13; instance SKUs `J757NAJEWXF7W9NH` ($0.674/hour), `SCWRBJEMR2B822WR` ($1.348/hour); gp3 SKUs `KYVYY29G957PKY3B` ($0.115), `J7S7KD4WFDNQWKNX` ($0.23); effective Nov 1. Extra backup storage $0.095/GiB-month |
| [S3 pricing](https://aws.amazon.com/s3/pricing/) and [S3 regional catalog](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-1/index.json) | Published Nov 16; SKUs `WP9ANXZGBYYSGJEA` (Standard first tier $0.023), `E9YHNFENF4XQBZR6` (PUT/LIST), `ZWQ6Q48CRJXX4FXE` (GET); effective Nov 1 |
| [ALB pricing](https://aws.amazon.com/elasticloadbalancing/pricing/) | $0.0225/hour, $0.008/LCU-hour in the N. Virginia examples |
| [PrivateLink pricing](https://aws.amazon.com/privatelink/pricing/) | $0.01/interface endpoint-AZ-hour and $0.01/GB in the first processing tier |
| [VPC pricing](https://aws.amazon.com/vpc/pricing/) and [gateway endpoint documentation](https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html) | Public IPv4 $0.005/hour; NAT $0.045/hour and $0.045/GB; no added gateway endpoint charge |
| [CloudWatch pricing](https://aws.amazon.com/cloudwatch/pricing/) | Log retention/ingestion and alarm budget; $10 is an allowance, not a service flat fee |
| [ECR pricing](https://aws.amazon.com/ecr/pricing/) | Private repository storage $0.10/GB-month |
| [Secrets Manager pricing](https://aws.amazon.com/secrets-manager/pricing/) | $0.40/secret-month, $0.05/10,000 API calls |
| [ACM pricing](https://aws.amazon.com/certificate-manager/pricing/) and [IAM pricing](https://aws.amazon.com/iam/) | No separate charge for the selected non-exportable public certificate and IAM roles |
| [Data transfer pricing](https://aws.amazon.com/ec2/pricing/on-demand/#Data_Transfer) | Shared internet-egress allowance and transfer rules; actual network bill depends on traffic paths |

Before spending money, recheck the configuration in the
[AWS Pricing Calculator](https://calculator.aws/), measure a representative load,
and set a billing budget/alarm. No AWS resources were created for this estimate.
