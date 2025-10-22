# Nimbus Copilot - UI Overview

## Main Interface

The Nimbus Copilot application features a modern, intuitive Streamlit interface with three main tabs:

### 1. 💬 Chat Tab

The chat interface is the primary way to interact with the AI agents:

```
┌─────────────────────────────────────────────────────────────────┐
│ ☁️ Nimbus Copilot                                               │
│ Your personal AI DevOps team for AWS: deploy faster, understand │
│ bills, and cut costs                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ 🤖 AI Agents                    │  Chat Messages                │
│ ────────────────                │  ─────────────────            │
│ Select Agent: [Auto-Select ▼]  │                                │
│                                  │  👤 User:                     │
│ Agent Capabilities               │  How can I reduce my AWS      │
│                                  │  costs?                       │
│ 🛠️ Setup Buddy                  │                                │
│ Infrastructure setup,            │  🤖 Assistant:                │
│ CloudFormation, deployment       │  I can help you identify      │
│                                  │  cost optimization            │
│ 📚 Doc Navigator                 │  opportunities...             │
│ AWS documentation, guides,       │                                │
│ best practices                   │  [📊 Cost Optimizer]          │
│                                  │  [🔌 Friendli.ai] [⚡ 245ms]  │
│ 💰 Bill Explainer                │                                │
│ Understand charges, billing      │  💭 Reasoning: Query about    │
│ breakdown                        │  cost optimization →          │
│                                  │  routed to Cost Optimizer     │
│ 📊 Cost Optimizer                │                                │
│ Cost reduction, savings          │  ────────────────────────     │
│ recommendations                  │                                │
│                                  │  [Ask me anything about AWS...]│
│ ────────────────                │                                │
│ 💰 Potential Savings             │                                │
│  $1,693.60/month                │                                │
│                                  │                                │
│ ────────────────                │                                │
│ ☑ Use Mock Data                 │                                │
└──────────────────────────────────┴────────────────────────────────┘
```

**Key Features:**
- Agent badges showing which specialist handled the query
- Provider badges showing LLM used (Friendli.ai or AWS Bedrock)
- Latency badges showing response time
- Reasoning traces explaining agent selection
- Auto-routing or manual agent selection

### 2. 🛠️ Tools Tab

The tools tab provides infrastructure generation capabilities:

```
┌─────────────────────────────────────────────────────────────────┐
│ 🏗️ CloudFormation Generator   │   🎨 Architecture Diagram      │
│                                 │                                │
│ Describe your infrastructure:   │   Describe your architecture: │
│ ┌─────────────────────────────┐ │   ┌──────────────────────────┐│
│ │ I need a VPC with EC2       │ │   │ Web app with load        ││
│ │ instances and an RDS        │ │   │ balancer, EC2 instances, ││
│ │ database                    │ │   │ and RDS                  ││
│ └─────────────────────────────┘ │   └──────────────────────────┘│
│                                 │                                │
│ [Generate CloudFormation]       │   [Generate Diagram]          │
│                                 │                                │
│ Generated Template:             │   Generated Diagram:          │
│ ┌─────────────────────────────┐ │   ┌──────────────────────────┐│
│ │AWSTemplateFormatVersion:    │ │   │ {                        ││
│ │  '2010-09-09'               │ │   │   "type": "excalidraw",  ││
│ │Description: VPC with EC2... │ │   │   "elements": [...]      ││
│ │Parameters:                  │ │   │ }                        ││
│ │  EnvironmentName:           │ │   └──────────────────────────┘│
│ │    Type: String             │ │                                │
│ │    Default: dev             │ │   [Open in Excalidraw]        │
│ │Resources:                   │ │   [Download Diagram JSON]     │
│ │  MainVPC:                   │ │                                │
│ │    Type: AWS::EC2::VPC      │ │                                │
│ │    Properties:              │ │                                │
│ │      CidrBlock: 10.0.0.0/16 │ │                                │
│ └─────────────────────────────┘ │                                │
│                                 │                                │
│ [Download Template]             │                                │
└─────────────────────────────────┴────────────────────────────────┘
```

**Key Features:**
- Natural language to CloudFormation conversion
- Architecture diagram generation with Excalidraw
- Download templates and diagrams
- Open diagrams directly in Excalidraw

### 3. 📊 Cost Analysis Tab

The cost analysis tab shows AWS cost breakdown and optimization opportunities:

```
┌─────────────────────────────────────────────────────────────────┐
│ 💰 Cost Analysis & Optimization                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Total Monthly Cost              │  Optimization Opportunities    │
│ $2,845.67                       │                                │
│                                 │  Potential Monthly Savings     │
│ Cost by Service                 │  $1,693.60                    │
│ ─────────────────              │                                │
│ EC2:         $1,245.30          │  💡 Right-size Over-provisioned│
│ S3:          $456.80            │     EC2 Instances              │
│ RDS:         $678.90            │     Save $345.60 | Easy        │
│ Lambda:      $234.50            │     > Downgrade t3.medium to  │
│ CloudFront:  $156.20            │       t3.small                │
│ DynamoDB:    $73.97             │                                │
│                                 │  💡 Implement S3 Lifecycle     │
│ Top Resources by Cost           │     Policies                   │
│ ─────────────────              │     Save $234.80 | Easy        │
│ EC2/web-server-prod             │     > Create lifecycle rule   │
│   Cost: $456.78                 │       to transition data      │
│   Utilization: 35%              │                                │
│                                 │  💡 Purchase Reserved Instances│
│ RDS/postgres-db                 │     Save $567.00 | Medium     │
│   Cost: $234.56                 │     > Purchase 1-year RI      │
│   Utilization: 68%              │                                │
│                                 │  💡 Delete Unused EBS Volumes  │
│ S3/data-lake-bucket             │     Save $89.50 | Easy         │
│   Cost: $189.34                 │     > Review and delete       │
│   Utilization: 90%              │       unused volumes          │
│                                 │                                │
│                                 │  💡 Enable Auto-scaling        │
│                                 │     Save $456.70 | Medium     │
│                                 │     > Configure auto-scaling  │
│                                 │       groups                  │
└─────────────────────────────────┴────────────────────────────────┘
```

**Key Features:**
- Total monthly cost overview
- Cost breakdown by service
- Top resources by cost with utilization
- Actionable optimization recommendations
- Estimated savings for each opportunity
- Difficulty rating for each recommendation

## UI Components

### Agent Badges
- **🛠️ Setup Buddy** - Blue badge
- **📚 Doc Navigator** - Purple badge
- **💰 Bill Explainer** - Orange badge
- **📊 Cost Optimizer** - Green badge

### Metadata Badges
- **Provider Badge** - Shows which LLM provider was used (Friendli.ai, AWS Bedrock, or mock)
- **Latency Badge** - Shows response time in milliseconds

### Savings Meter
A prominent green gradient display showing total potential monthly savings:
```
┌──────────────────────────┐
│   💰 Potential Savings   │
│    $1,693.60/month      │
└──────────────────────────┘
```

### Reasoning Trace
Shows the logic behind agent selection:
```
┌──────────────────────────────────────────────┐
│ 💭 Reasoning: Query about cost optimization │
│    → routed to Cost Optimizer               │
└──────────────────────────────────────────────┘
```

## Color Scheme

- **Primary Gradient**: Purple to Blue (#667eea to #764ba2)
- **Setup Buddy**: Light Blue (#e3f2fd background, #1976d2 text)
- **Doc Navigator**: Light Purple (#f3e5f5 background, #7b1fa2 text)
- **Bill Explainer**: Light Orange (#fff3e0 background, #e65100 text)
- **Cost Optimizer**: Light Green (#e8f5e9 background, #2e7d32 text)
- **Savings Meter**: Green Gradient (#4caf50 to #8bc34a)

## Responsive Design

The application is fully responsive and works on:
- Desktop (1920x1080 and above)
- Laptop (1366x768 and above)
- Tablet (768x1024)
- Mobile (375x667 minimum)

Streamlit handles the responsive layout automatically, with the sidebar collapsing on smaller screens.
