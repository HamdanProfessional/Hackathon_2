"use client";

import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  MessageSquare,
  Mail,
  BarChart3,
  Wrench,
  RefreshCw,
} from "lucide-react";
import { apiClient } from "@/lib/api";
import { StatsCard } from "@/components/analytics/stats-card";
import {
  ConversationsChart,
  TimelineDataPoint,
} from "@/components/analytics/conversations-chart";
import { ToolUsageChart, ToolUsageStats } from "@/components/analytics/tool-usage-chart";
import {
  MessageDistribution,
  MessageRoleStats,
} from "@/components/analytics/message-distribution";

// Types
interface OverviewStats {
  total_conversations: number;
  total_messages: number;
  avg_messages_per_conversation: number;
  total_tool_calls: number;
}

interface TimelineData {
  period: string;
  data: TimelineDataPoint[];
  total_conversations: number;
}

interface ToolUsageData {
  total_tool_calls: number;
  tool_stats: ToolUsageStats[];
  most_used_tool: string | null;
}

interface MessageDistributionData {
  total_messages: number;
  distribution: MessageRoleStats[];
}

type Period = "daily" | "weekly" | "monthly";

export default function ConversationAnalyticsPage() {
  const [overview, setOverview] = useState<OverviewStats | null>(null);
  const [timelineData, setTimelineData] = useState<TimelineData | null>(null);
  const [toolUsage, setToolUsage] = useState<ToolUsageData | null>(null);
  const [messageDistribution, setMessageDistribution] =
    useState<MessageDistributionData | null>(null);
  const [period, setPeriod] = useState<Period>("daily");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, [period]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      const [overviewData, timeline, tools, messages] = await Promise.all([
        apiClient.getChatOverview(),
        apiClient.getConversationsTimeline(period),
        apiClient.getToolUsage(),
        apiClient.getMessageDistribution(),
      ]);

      setOverview(overviewData);
      setTimelineData(timeline);
      setToolUsage(tools);
      setMessageDistribution(messages);
    } catch (err: any) {
      console.error("Failed to load analytics:", err);
      setError(err.response?.data?.detail || err.message || "Failed to load analytics");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Conversation Analytics</h1>
          <p className="text-muted-foreground">
            View insights about your AI chat conversations
          </p>
        </div>

        {/* Skeleton loaders */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="glass-card">
              <CardContent className="pt-6">
                <div className="animate-pulse h-24 bg-muted/50 rounded-lg" />
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="glass-card">
              <CardContent className="pt-6">
                <div className="animate-pulse h-64 bg-muted/50 rounded-lg" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Conversation Analytics</h1>
          <p className="text-muted-foreground">
            View insights about your AI chat conversations
          </p>
        </div>

        <Card className="glass-card border-destructive/50">
          <CardContent className="pt-6">
            <div className="text-center py-8">
              <p className="text-destructive mb-4">Failed to load analytics: {error}</p>
              <Button onClick={loadAnalytics} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!overview || !timelineData || !toolUsage || !messageDistribution) {
    return null;
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Conversation Analytics</h1>
          <p className="text-muted-foreground">
            View insights about your AI chat conversations
          </p>
        </div>
        <Button onClick={loadAnalytics} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Stats Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatsCard
          title="Total Conversations"
          value={overview.total_conversations}
          icon={MessageSquare}
          color="primary"
          description="All-time conversations"
        />
        <StatsCard
          title="Total Messages"
          value={overview.total_messages}
          icon={Mail}
          color="success"
          description="Across all conversations"
        />
        <StatsCard
          title="Avg Messages/Conversation"
          value={overview.avg_messages_per_conversation.toFixed(1)}
          icon={BarChart3}
          color="warning"
          description="Average conversation length"
        />
        <StatsCard
          title="Total Tool Calls"
          value={overview.total_tool_calls}
          icon={Wrench}
          color="default"
          description="AI assistant actions"
        />
      </div>

      {/* Period Selector */}
      <div className="flex items-center gap-2 mb-6">
        <span className="text-sm text-muted-foreground">Timeline:</span>
        <div className="flex gap-1">
          {(["daily", "weekly", "monthly"] as Period[]).map((p) => (
            <Button
              key={p}
              variant={period === p ? "default" : "outline"}
              size="sm"
              onClick={() => setPeriod(p)}
              className="capitalize"
            >
              {p}
            </Button>
          ))}
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Conversations Timeline Chart */}
        <ConversationsChart
          data={timelineData.data}
          period={timelineData.period as Period}
          className="lg:col-span-2"
        />

        {/* Tool Usage Chart */}
        <ToolUsageChart
          data={toolUsage.tool_stats}
          totalToolCalls={toolUsage.total_tool_calls}
        />

        {/* Message Distribution */}
        <MessageDistribution
          data={messageDistribution.distribution}
          totalMessages={messageDistribution.total_messages}
        />
      </div>
    </div>
  );
}
