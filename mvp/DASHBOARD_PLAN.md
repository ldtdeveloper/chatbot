# Dashboard Screen Plan

## Overview
The Dashboard will display analytics and usage statistics for the user's OpenAI API keys, helping them monitor interactions, expenses, and performance.

## Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│  Dashboard Header                                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Graph 1: Interactions (per OpenAI API Key)           │  │
│  │  Full Width - Line/Area Chart                        │  │
│  │  Shows: Daily/Weekly/Monthly interaction counts      │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────┐ ┌───────────────────┐  │
│  │  Graph 2: Expenses               │ │  Graph 3:         │  │
│  │  (per OpenAI API Key)            │ │  Active Agents    │  │
│  │  50% Width - Bar Chart           │ │  50% Width        │  │
│  │  Shows: Cost per key over time   │ │  Pie/Doughnut     │  │
│  └──────────────────────────────────┘ └───────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Graph Details

### 1. Interactions Graph (Full Width)
- **Type**: Line Chart or Area Chart
- **Data**: Number of interactions per OpenAI API key over time
- **Time Range**: Last 7 days, 30 days, 90 days (selectable)
- **Grouping**: Per OpenAI API key (different colors/lines)
- **Metrics**:
  - Total interactions
  - Successful interactions
  - Failed interactions (if applicable)
- **Features**:
  - Date range selector (7d, 30d, 90d, custom)
  - Key selector (all keys or specific key)
  - Hover tooltips showing exact counts
  - Legend showing all keys

### 2. Expenses Graph (50% Width)
- **Type**: Bar Chart or Stacked Bar Chart
- **Data**: Cost/expenses per OpenAI API key
- **Time Range**: Last 7 days, 30 days, 90 days (selectable)
- **Grouping**: Per OpenAI API key (stacked or grouped bars)
- **Metrics**:
  - Total cost per key
  - Cost breakdown by model (if available)
  - Estimated cost based on usage
- **Features**:
  - Date range selector
  - Currency display (USD)
  - Hover tooltips showing exact costs
  - Color coding per key

### 3. Active Agents Graph (50% Width) - SUGGESTED
- **Type**: Pie Chart or Doughnut Chart
- **Data**: Distribution of agents per OpenAI API key
- **Metrics**:
  - Number of active agents per key
  - Percentage distribution
  - Total active agents count
- **Features**:
  - Interactive segments (click to filter)
  - Legend with counts
  - Center text showing total agents
- **Alternative Suggestions**:
  - **Response Time Graph**: Average response time per key (Line/Bar)
  - **Usage by Agent**: Top 5 agents by interaction count (Horizontal Bar)
  - **Success Rate**: Success vs failure rate per key (Stacked Bar)

## Database Model Design

### New Model: `api_usage_log`

```python
class APIUsageLog(Base):
    __tablename__ = "api_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    openai_key_id = Column(Integer, ForeignKey("openai_keys.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)  # Optional
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Interaction details
    interaction_type = Column(String, nullable=False)  # 'websocket_session', 'api_call', etc.
    status = Column(String, nullable=False)  # 'success', 'failed', 'error'
    duration_ms = Column(Integer, nullable=True)  # Session duration in milliseconds
    
    # Cost tracking
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)  # Calculated cost
    
    # Model information
    model_used = Column(String, nullable=True)  # e.g., 'gpt-4o-realtime-preview-2024-12-17'
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    openai_key = relationship("OpenAIKey", back_populates="usage_logs")
    agent = relationship("Agent", back_populates="usage_logs")
    user = relationship("User")
```

### Model Updates Required

**Update `OpenAIKey` model:**
```python
usage_logs = relationship("APIUsageLog", back_populates="openai_key")
```

**Update `Agent` model:**
```python
usage_logs = relationship("APIUsageLog", back_populates="agent")
```

## Backend API Endpoints

### 1. Get Interactions Data
```
GET /api/analytics/interactions
Query Parameters:
  - openai_key_id (optional): Filter by specific key
  - start_date (optional): ISO date string
  - end_date (optional): ISO date string
  - group_by: 'day' | 'week' | 'month' (default: 'day')

Response:
{
  "data": [
    {
      "date": "2024-01-15",
      "openai_key_id": 1,
      "key_name": "Production Key",
      "total_interactions": 150,
      "successful": 145,
      "failed": 5
    },
    ...
  ],
  "summary": {
    "total_interactions": 1500,
    "total_successful": 1450,
    "total_failed": 50
  }
}
```

### 2. Get Expenses Data
```
GET /api/analytics/expenses
Query Parameters:
  - openai_key_id (optional): Filter by specific key
  - start_date (optional): ISO date string
  - end_date (optional): ISO date string
  - group_by: 'day' | 'week' | 'month' (default: 'day')

Response:
{
  "data": [
    {
      "date": "2024-01-15",
      "openai_key_id": 1,
      "key_name": "Production Key",
      "total_cost_usd": 12.50,
      "input_tokens": 50000,
      "output_tokens": 30000,
      "total_tokens": 80000
    },
    ...
  ],
  "summary": {
    "total_cost_usd": 125.75,
    "total_tokens": 800000
  }
}
```

### 3. Get Active Agents Data
```
GET /api/analytics/active-agents

Response:
{
  "data": [
    {
      "openai_key_id": 1,
      "key_name": "Production Key",
      "agent_count": 5,
      "percentage": 50.0
    },
    {
      "openai_key_id": 2,
      "key_name": "Development Key",
      "agent_count": 5,
      "percentage": 50.0
    }
  ],
  "total_agents": 10
}
```

### 4. Get Dashboard Summary
```
GET /api/analytics/summary
Query Parameters:
  - period: '7d' | '30d' | '90d' (default: '30d')

Response:
{
  "period": "30d",
  "total_interactions": 1500,
  "total_cost_usd": 125.75,
  "total_agents": 10,
  "active_keys": 2,
  "top_key": {
    "id": 1,
    "name": "Production Key",
    "interactions": 1000,
    "cost": 100.50
  }
}
```

## Frontend Implementation

### Chart Library: Recharts
**Why Recharts?**
- Built for React
- Lightweight and performant
- Good TypeScript support
- Responsive by default
- Easy to customize

**Installation:**
```bash
npm install recharts
```

### Component Structure

```
Dashboard.jsx
├── DashboardHeader (title, date range selector)
├── InteractionsChart (full width)
│   ├── DateRangeSelector
│   ├── KeyFilter
│   └── LineChart/AreaChart (Recharts)
├── BottomRow (flex container)
│   ├── ExpensesChart (50% width)
│   │   ├── DateRangeSelector
│   │   └── BarChart (Recharts)
│   └── ActiveAgentsChart (50% width)
│       └── PieChart/DoughnutChart (Recharts)
└── SummaryCards (optional - quick stats)
```

### Data Fetching
- Use TanStack Query for data fetching
- Implement caching (5 minutes)
- Loading states for each chart
- Error handling with retry

### Styling
- Responsive design (mobile-friendly)
- Card-based layout with shadows
- Consistent color scheme
- Loading skeletons

## Implementation Steps

1. **Backend:**
   - [ ] Create `APIUsageLog` model
   - [ ] Update existing models with relationships
   - [ ] Create database migration
   - [ ] Implement logging in widget WebSocket handler
   - [ ] Create analytics routes (`/api/analytics/*`)
   - [ ] Implement cost calculation logic

2. **Frontend:**
   - [ ] Install Recharts library
   - [ ] Create Dashboard service functions
   - [ ] Build InteractionsChart component
   - [ ] Build ExpensesChart component
   - [ ] Build ActiveAgentsChart component
   - [ ] Integrate all charts in Dashboard
   - [ ] Add date range selectors
   - [ ] Add loading/error states
   - [ ] Style and make responsive

3. **Testing:**
   - [ ] Test with multiple API keys
   - [ ] Test with different date ranges
   - [ ] Test responsive design
   - [ ] Test loading states
   - [ ] Test error handling

## Cost Calculation

For OpenAI Realtime API, cost calculation:
- **Input tokens**: Based on audio input duration and model
- **Output tokens**: Based on audio output duration and model
- **Model pricing**: 
  - `gpt-4o-realtime-preview-2024-12-17`: $0.015 per 1K input tokens, $0.060 per 1K output tokens
  - Update pricing as OpenAI changes rates

**Formula:**
```
cost = (input_tokens / 1000 * input_price) + (output_tokens / 1000 * output_price)
```

## Future Enhancements

1. Export data (CSV/PDF)
2. Email reports (daily/weekly/monthly)
3. Alerts for high usage/costs
4. Budget limits and warnings
5. Agent-level analytics
6. Real-time updates (WebSocket)
7. Comparison views (period over period)
8. Custom date ranges with calendar picker

