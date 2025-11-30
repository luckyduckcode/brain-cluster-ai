#!/usr/bin/env python3
"""
Observability Dashboard for Brain Cluster AI
Provides real-time visualization of brain activity, consensus decisions, and system metrics.
"""

import streamlit as st
import requests
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import threading
import queue
import json
from typing import Dict, List, Any, Optional

class BrainObservabilityDashboard:
    """Real-time observability dashboard for the Brain Cluster AI system."""

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.metrics_queue = queue.Queue()
        self.is_monitoring = False
        self.monitor_thread = None

        # Initialize session state for persistent data
        if 'metrics_history' not in st.session_state:
            st.session_state.metrics_history = []
        if 'alerts' not in st.session_state:
            st.session_state.alerts = []
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()

    def start_monitoring(self):
        """Start background monitoring thread."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop background monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)

    def _monitor_loop(self):
        """Background monitoring loop that collects metrics."""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                if metrics:
                    self.metrics_queue.put(metrics)
                time.sleep(2)  # Update every 2 seconds
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)  # Wait longer on error

    def _collect_metrics(self) -> Optional[Dict[str, Any]]:
        """Collect current system metrics from the API."""
        try:
            # Get system status
            status_response = requests.get(f"{self.api_base_url}/api/v1/status", timeout=5)
            if status_response.status_code != 200:
                return None

            status_data = status_response.json()

            # Get recent memories for activity analysis
            memories_response = requests.get(f"{self.api_base_url}/api/v1/memories", timeout=5)
            memories_data = memories_response.json() if memories_response.status_code == 200 else []

            # Calculate derived metrics
            metrics = {
                'timestamp': datetime.now(),
                'system_status': status_data.get('status', 'unknown'),
                'uptime_seconds': status_data.get('uptime_seconds', 0),
                'total_queries': status_data.get('total_queries', 0),
                'active_neurons': status_data.get('active_neurons', 0),
                'memory_count': len(memories_data),
                'cache_hit_rate': status_data.get('cache_hit_rate', 0.0),
                'avg_response_time': status_data.get('avg_response_time', 0.0),
                'error_rate': status_data.get('error_rate', 0.0),
                'consensus_confidence': status_data.get('consensus_confidence', 0.0),
                'memory_connections': sum(len(m.get('connections', [])) for m in memories_data),
            }

            return metrics

        except requests.RequestException:
            return None

    def get_latest_metrics(self) -> Optional[Dict[str, Any]]:
        """Get the most recent metrics from the queue."""
        try:
            while not self.metrics_queue.empty():
                latest = self.metrics_queue.get_nowait()
                st.session_state.metrics_history.append(latest)
                # Keep only last 1000 data points
                if len(st.session_state.metrics_history) > 1000:
                    st.session_state.metrics_history = st.session_state.metrics_history[-1000:]
                return latest
        except queue.Empty:
            pass
        return None

    def create_dashboard(self):
        """Create the main Streamlit dashboard."""
        st.set_page_config(
            page_title="Brain Cluster AI - Observability Dashboard",
            page_icon="🧠",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        st.title("🧠 Brain Cluster AI - Observability Dashboard")
        st.markdown("Real-time monitoring of cognitive processes and system health")

        # Sidebar controls
        with st.sidebar:
            st.header("Dashboard Controls")

            if st.button("▶️ Start Monitoring", type="primary"):
                self.start_monitoring()
                st.success("Monitoring started!")

            if st.button("⏹️ Stop Monitoring"):
                self.stop_monitoring()
                st.info("Monitoring stopped.")

            st.divider()

            # Connection status
            try:
                response = requests.get(f"{self.api_base_url}/api/v1/status", timeout=2)
                if response.status_code == 200:
                    st.success("✅ Connected to API")
                else:
                    st.error("❌ API connection failed")
            except:
                st.error("❌ Cannot connect to API")

            st.markdown(f"**API URL:** {self.api_base_url}")

            # Quick stats
            if st.session_state.metrics_history:
                latest = st.session_state.metrics_history[-1]
                st.metric("Total Queries", latest.get('total_queries', 0))
                st.metric("Active Neurons", latest.get('active_neurons', 0))
                st.metric("Memory Count", latest.get('memory_count', 0))

        # Main dashboard content
        if not st.session_state.metrics_history:
            st.info("Click 'Start Monitoring' to begin collecting metrics.")
            return

        # Get latest metrics
        latest_metrics = self.get_latest_metrics() or st.session_state.metrics_history[-1]

        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 System Overview", "🧠 Brain Activity", "💾 Memory Network", "⚠️ Alerts & Health"])

        with tab1:
            self._create_system_overview_tab(latest_metrics)

        with tab2:
            self._create_brain_activity_tab()

        with tab3:
            self._create_memory_network_tab()

        with tab4:
            self._create_alerts_health_tab(latest_metrics)

    def _create_system_overview_tab(self, latest_metrics: Dict[str, Any]):
        """Create the system overview tab."""
        st.header("System Overview")

        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            uptime_hours = latest_metrics.get('uptime_seconds', 0) / 3600
            st.metric(
                "System Uptime",
                f"{uptime_hours:.1f}h",
                delta=f"+{2/3600:.1f}h" if len(st.session_state.metrics_history) > 1 else None
            )

        with col2:
            st.metric(
                "Total Queries",
                latest_metrics.get('total_queries', 0),
                delta=self._calculate_delta('total_queries')
            )

        with col3:
            cache_rate = latest_metrics.get('cache_hit_rate', 0) * 100
            st.metric(
                "Cache Hit Rate",
                f"{cache_rate:.1f}%",
                delta=self._calculate_delta('cache_hit_rate', multiplier=100)
            )

        with col4:
            response_time = latest_metrics.get('avg_response_time', 0) * 1000
            st.metric(
                "Avg Response Time",
                f"{response_time:.0f}ms",
                delta=self._calculate_delta('avg_response_time', multiplier=1000)
            )

        st.divider()

        # Performance charts
        col1, col2 = st.columns(2)

        with col1:
            self._create_performance_chart()

        with col2:
            self._create_consensus_chart()

    def _create_brain_activity_tab(self):
        """Create the brain activity visualization tab."""
        st.header("Brain Activity")

        if len(st.session_state.metrics_history) < 2:
            st.info("Collecting more data for brain activity visualization...")
            return

        # Neuron activity over time
        df = pd.DataFrame(st.session_state.metrics_history)

        fig = px.line(
            df,
            x='timestamp',
            y='active_neurons',
            title='Active Neurons Over Time',
            labels={'active_neurons': 'Active Neurons', 'timestamp': 'Time'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Consensus confidence trend
        fig2 = px.line(
            df,
            x='timestamp',
            y='consensus_confidence',
            title='Consensus Confidence Trend',
            labels={'consensus_confidence': 'Confidence', 'timestamp': 'Time'}
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

    def _create_memory_network_tab(self):
        """Create the memory network visualization tab."""
        st.header("Memory Network")

        if not st.session_state.metrics_history:
            return

        latest = st.session_state.metrics_history[-1]

        # Memory statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Memories", latest.get('memory_count', 0))

        with col2:
            st.metric("Memory Connections", latest.get('memory_connections', 0))

        with col3:
            avg_connections = (latest.get('memory_connections', 0) / max(latest.get('memory_count', 1), 1))
            st.metric("Avg Connections per Memory", f"{avg_connections:.1f}")

        # Memory growth chart
        if len(st.session_state.metrics_history) > 1:
            df = pd.DataFrame(st.session_state.metrics_history)
            fig = px.line(
                df,
                x='timestamp',
                y='memory_count',
                title='Memory Growth Over Time',
                labels={'memory_count': 'Memory Count', 'timestamp': 'Time'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    def _create_alerts_health_tab(self, latest_metrics: Dict[str, Any]):
        """Create the alerts and health monitoring tab."""
        st.header("System Health & Alerts")

        # Health indicators
        health_indicators = {
            "API Connectivity": self._check_api_health(),
            "Cache Performance": "healthy" if latest_metrics.get('cache_hit_rate', 0) > 0.5 else "warning",
            "Response Time": "healthy" if latest_metrics.get('avg_response_time', 0) < 2.0 else "warning",
            "Error Rate": "healthy" if latest_metrics.get('error_rate', 0) < 0.05 else "critical",
            "Consensus Confidence": "healthy" if latest_metrics.get('consensus_confidence', 0) > 0.7 else "warning"
        }

        for indicator, status in health_indicators.items():
            if status == "healthy":
                st.success(f"✅ {indicator}: Healthy")
            elif status == "warning":
                st.warning(f"⚠️ {indicator}: Warning")
            else:
                st.error(f"❌ {indicator}: Critical")

        st.divider()

        # Recent alerts
        st.subheader("Recent Alerts")
        if st.session_state.alerts:
            for alert in st.session_state.alerts[-5:]:  # Show last 5 alerts
                st.write(f"{alert['timestamp']}: {alert['message']}")
        else:
            st.info("No recent alerts")

    def _check_api_health(self) -> str:
        """Check API connectivity health."""
        try:
            response = requests.get(f"{self.api_base_url}/api/v1/status", timeout=2)
            return "healthy" if response.status_code == 200 else "critical"
        except:
            return "critical"

    def _calculate_delta(self, metric: str, multiplier: float = 1.0) -> Optional[float]:
        """Calculate the delta for a metric compared to previous measurement."""
        if len(st.session_state.metrics_history) < 2:
            return None

        current = st.session_state.metrics_history[-1].get(metric, 0) * multiplier
        previous = st.session_state.metrics_history[-2].get(metric, 0) * multiplier
        return current - previous

    def _create_performance_chart(self):
        """Create a performance metrics chart."""
        if len(st.session_state.metrics_history) < 2:
            return

        df = pd.DataFrame(st.session_state.metrics_history[-50:])  # Last 50 data points

        fig = go.Figure()

        # Response time
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['avg_response_time'] * 1000,
            name='Response Time (ms)',
            line=dict(color='blue')
        ))

        # Cache hit rate
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['cache_hit_rate'] * 100,
            name='Cache Hit Rate (%)',
            yaxis='y2',
            line=dict(color='green')
        ))

        fig.update_layout(
            title='Performance Metrics',
            xaxis=dict(title='Time'),
            yaxis=dict(title='Response Time (ms)', titlefont=dict(color='blue')),
            yaxis2=dict(title='Cache Hit Rate (%)', titlefont=dict(color='green'),
                       overlaying='y', side='right'),
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    def _create_consensus_chart(self):
        """Create a consensus confidence chart."""
        if len(st.session_state.metrics_history) < 2:
            return

        df = pd.DataFrame(st.session_state.metrics_history[-50:])  # Last 50 data points

        fig = px.line(
            df,
            x='timestamp',
            y='consensus_confidence',
            title='Consensus Confidence Over Time',
            labels={'consensus_confidence': 'Confidence Score', 'timestamp': 'Time'}
        )

        # Add threshold line
        fig.add_hline(y=0.7, line_dash="dash", line_color="red",
                     annotation_text="Confidence Threshold")

        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


def main():
    """Main entry point for the observability dashboard."""
    # Initialize dashboard
    dashboard = BrainObservabilityDashboard()

    # Create the dashboard
    dashboard.create_dashboard()

    # Auto-refresh every 2 seconds when monitoring is active
    if dashboard.is_monitoring:
        time.sleep(2)
        st.rerun()


if __name__ == "__main__":
    main()