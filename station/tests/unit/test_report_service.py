"""
Unit tests for ReportService and report generators.
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from station_service.api.schemas.report import (
    ReportType,
    PeriodType,
    BatchSummaryReport,
    PeriodStatisticsReport,
    StepAnalysisReport,
)
from station_service.services.report_service import (
    ReportService,
    BatchSummaryReportGenerator,
    PeriodStatisticsReportGenerator,
    StepAnalysisReportGenerator,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_database():
    """Create a mock database with execution repository."""
    db = MagicMock()
    db.execution_repository = AsyncMock()
    return db


@pytest.fixture
def sample_batch_statistics():
    """Sample batch statistics data."""
    return {
        "total": 100,
        "pass_count": 85,
        "fail_count": 15,
        "avg_duration": 5.5,
        "min_duration": 2.0,
        "max_duration": 12.0,
        "first_execution": datetime.now() - timedelta(days=7),
        "last_execution": datetime.now(),
    }


@pytest.fixture
def sample_step_statistics():
    """Sample step statistics data."""
    return [
        {
            "step_name": "Initialize",
            "total_runs": 100,
            "pass_count": 98,
            "fail_count": 2,
            "avg_duration": 1.2,
            "min_duration": 0.8,
            "max_duration": 2.5,
        },
        {
            "step_name": "Execute Test",
            "total_runs": 100,
            "pass_count": 90,
            "fail_count": 10,
            "avg_duration": 3.5,
            "min_duration": 1.5,
            "max_duration": 8.0,
        },
        {
            "step_name": "Cleanup",
            "total_runs": 100,
            "pass_count": 100,
            "fail_count": 0,
            "avg_duration": 0.5,
            "min_duration": 0.3,
            "max_duration": 1.0,
        },
    ]


@pytest.fixture
def sample_period_statistics():
    """Sample period statistics data."""
    base_date = datetime.now() - timedelta(days=7)
    return [
        {
            "period_start": base_date,
            "period_end": base_date + timedelta(days=1),
            "total": 15,
            "pass_count": 12,
            "fail_count": 3,
            "avg_duration": 5.0,
        },
        {
            "period_start": base_date + timedelta(days=1),
            "period_end": base_date + timedelta(days=2),
            "total": 20,
            "pass_count": 18,
            "fail_count": 2,
            "avg_duration": 4.8,
        },
        {
            "period_start": base_date + timedelta(days=2),
            "period_end": base_date + timedelta(days=3),
            "total": 18,
            "pass_count": 17,
            "fail_count": 1,
            "avg_duration": 5.2,
        },
    ]


@pytest.fixture
def sample_step_analysis():
    """Sample step analysis data."""
    return [
        {
            "step_name": "Execute Test",
            "total_runs": 100,
            "fail_count": 10,
            "avg_duration": 3500,
            "min_duration": 1500,
            "max_duration": 8000,
            "durations": [3000, 3200, 3500, 3800, 4000, 4200, 4500, 5000, 6000, 8000],
        },
        {
            "step_name": "Initialize",
            "total_runs": 100,
            "fail_count": 2,
            "avg_duration": 1200,
            "min_duration": 800,
            "max_duration": 2500,
            "durations": [800, 900, 1000, 1100, 1200, 1300, 1400, 1800, 2000, 2500],
        },
    ]


@pytest.fixture
def sample_failure_reasons():
    """Sample failure reasons data."""
    return [
        {"error_message": "Timeout exceeded", "count": 5},
        {"error_message": "Connection failed", "count": 3},
        {"error_message": "Validation error", "count": 2},
    ]


# ============================================================================
# ReportService Tests
# ============================================================================


class TestReportService:
    """Tests for ReportService factory."""

    def test_get_generator_batch_summary(self, mock_database):
        """Test getting BatchSummaryReportGenerator."""
        service = ReportService(mock_database)
        generator = service.get_generator(ReportType.BATCH_SUMMARY)

        assert isinstance(generator, BatchSummaryReportGenerator)

    def test_get_generator_period_stats(self, mock_database):
        """Test getting PeriodStatisticsReportGenerator."""
        service = ReportService(mock_database)
        generator = service.get_generator(ReportType.PERIOD_STATS)

        assert isinstance(generator, PeriodStatisticsReportGenerator)

    def test_get_generator_step_analysis(self, mock_database):
        """Test getting StepAnalysisReportGenerator."""
        service = ReportService(mock_database)
        generator = service.get_generator(ReportType.STEP_ANALYSIS)

        assert isinstance(generator, StepAnalysisReportGenerator)

    def test_get_generator_invalid_type(self, mock_database):
        """Test getting generator with invalid type raises ValueError."""
        service = ReportService(mock_database)

        with pytest.raises(ValueError, match="Unknown report type"):
            service.get_generator("invalid_type")

    def test_register_custom_generator(self, mock_database):
        """Test registering a custom generator."""
        class CustomGenerator:
            def __init__(self, db):
                self.db = db

            async def generate(self, **kwargs):
                return {"custom": True}

        ReportService.register_generator("custom_report", CustomGenerator)

        service = ReportService(mock_database)
        generator = service.get_generator("custom_report")

        assert isinstance(generator, CustomGenerator)

        # Cleanup
        del ReportService._generators["custom_report"]


# ============================================================================
# BatchSummaryReportGenerator Tests
# ============================================================================


class TestBatchSummaryReportGenerator:
    """Tests for BatchSummaryReportGenerator."""

    @pytest.mark.asyncio
    async def test_generate_success(
        self,
        mock_database,
        sample_batch_statistics,
        sample_step_statistics,
    ):
        """Test successful batch summary report generation."""
        mock_database.execution_repository.get_batch_statistics = AsyncMock(
            return_value=sample_batch_statistics
        )
        mock_database.execution_repository.get_step_statistics_by_batch = AsyncMock(
            return_value=sample_step_statistics
        )

        generator = BatchSummaryReportGenerator(mock_database)
        report = await generator.generate(
            batch_id="batch-001",
            batch_name="Test Batch",
        )

        assert isinstance(report, BatchSummaryReport)
        assert report.batch_id == "batch-001"
        assert report.batch_name == "Test Batch"
        assert report.total_executions == 100
        assert report.pass_count == 85
        assert report.fail_count == 15
        assert report.pass_rate == 0.85
        assert len(report.steps) == 3

    @pytest.mark.asyncio
    async def test_generate_empty_batch(self, mock_database):
        """Test report generation for empty batch."""
        mock_database.execution_repository.get_batch_statistics = AsyncMock(
            return_value={
                "total": 0,
                "pass_count": 0,
                "fail_count": 0,
                "avg_duration": 0,
                "min_duration": 0,
                "max_duration": 0,
                "first_execution": None,
                "last_execution": None,
            }
        )
        mock_database.execution_repository.get_step_statistics_by_batch = AsyncMock(
            return_value=[]
        )

        generator = BatchSummaryReportGenerator(mock_database)
        report = await generator.generate(batch_id="empty-batch")

        assert report.total_executions == 0
        assert report.pass_rate == 0.0
        assert len(report.steps) == 0

    @pytest.mark.asyncio
    async def test_generate_calculates_pass_rate_correctly(self, mock_database):
        """Test that pass rate is calculated correctly."""
        mock_database.execution_repository.get_batch_statistics = AsyncMock(
            return_value={
                "total": 10,
                "pass_count": 7,
                "fail_count": 3,
                "avg_duration": 5.0,
                "min_duration": 2.0,
                "max_duration": 8.0,
                "first_execution": datetime.now(),
                "last_execution": datetime.now(),
            }
        )
        mock_database.execution_repository.get_step_statistics_by_batch = AsyncMock(
            return_value=[]
        )

        generator = BatchSummaryReportGenerator(mock_database)
        report = await generator.generate(batch_id="batch-001")

        assert report.pass_rate == 0.7


# ============================================================================
# PeriodStatisticsReportGenerator Tests
# ============================================================================


class TestPeriodStatisticsReportGenerator:
    """Tests for PeriodStatisticsReportGenerator."""

    @pytest.mark.asyncio
    async def test_generate_daily(self, mock_database, sample_period_statistics):
        """Test daily period statistics generation."""
        mock_database.execution_repository.get_period_statistics = AsyncMock(
            return_value=sample_period_statistics
        )

        generator = PeriodStatisticsReportGenerator(mock_database)
        from_date = datetime.now() - timedelta(days=7)
        to_date = datetime.now()

        report = await generator.generate(
            period_type=PeriodType.DAILY,
            from_date=from_date,
            to_date=to_date,
        )

        assert isinstance(report, PeriodStatisticsReport)
        assert report.period_type == PeriodType.DAILY
        assert len(report.data_points) == 3
        assert report.total_executions == 53  # 15 + 20 + 18

    @pytest.mark.asyncio
    async def test_generate_calculates_trend_increasing(self, mock_database):
        """Test that trend is calculated as increasing."""
        # Pass rates: 0.6 -> 0.8 -> 0.9 (increasing)
        mock_database.execution_repository.get_period_statistics = AsyncMock(
            return_value=[
                {"period_start": datetime.now(), "period_end": datetime.now(),
                 "total": 10, "pass_count": 6, "fail_count": 4, "avg_duration": 5.0},
                {"period_start": datetime.now(), "period_end": datetime.now(),
                 "total": 10, "pass_count": 8, "fail_count": 2, "avg_duration": 5.0},
                {"period_start": datetime.now(), "period_end": datetime.now(),
                 "total": 10, "pass_count": 9, "fail_count": 1, "avg_duration": 5.0},
            ]
        )

        generator = PeriodStatisticsReportGenerator(mock_database)
        report = await generator.generate(
            period_type=PeriodType.DAILY,
            from_date=datetime.now() - timedelta(days=3),
            to_date=datetime.now(),
        )

        assert report.trend_direction == "increasing"

    @pytest.mark.asyncio
    async def test_generate_calculates_trend_decreasing(self, mock_database):
        """Test that trend is calculated as decreasing."""
        # Pass rates: 0.9 -> 0.7 -> 0.5 (decreasing)
        mock_database.execution_repository.get_period_statistics = AsyncMock(
            return_value=[
                {"period_start": datetime.now(), "period_end": datetime.now(),
                 "total": 10, "pass_count": 9, "fail_count": 1, "avg_duration": 5.0},
                {"period_start": datetime.now(), "period_end": datetime.now(),
                 "total": 10, "pass_count": 7, "fail_count": 3, "avg_duration": 5.0},
                {"period_start": datetime.now(), "period_end": datetime.now(),
                 "total": 10, "pass_count": 5, "fail_count": 5, "avg_duration": 5.0},
            ]
        )

        generator = PeriodStatisticsReportGenerator(mock_database)
        report = await generator.generate(
            period_type=PeriodType.DAILY,
            from_date=datetime.now() - timedelta(days=3),
            to_date=datetime.now(),
        )

        assert report.trend_direction == "decreasing"

    @pytest.mark.asyncio
    async def test_generate_with_batch_filter(self, mock_database, sample_period_statistics):
        """Test period statistics with batch filter."""
        mock_database.execution_repository.get_period_statistics = AsyncMock(
            return_value=sample_period_statistics
        )

        generator = PeriodStatisticsReportGenerator(mock_database)
        report = await generator.generate(
            period_type=PeriodType.DAILY,
            from_date=datetime.now() - timedelta(days=7),
            to_date=datetime.now(),
            batch_id="specific-batch",
        )

        # Verify batch_id was passed to repository
        mock_database.execution_repository.get_period_statistics.assert_called_once()
        call_kwargs = mock_database.execution_repository.get_period_statistics.call_args[1]
        assert call_kwargs.get("batch_id") == "specific-batch"


# ============================================================================
# StepAnalysisReportGenerator Tests
# ============================================================================


class TestStepAnalysisReportGenerator:
    """Tests for StepAnalysisReportGenerator."""

    @pytest.mark.asyncio
    async def test_generate_success(
        self,
        mock_database,
        sample_step_analysis,
        sample_failure_reasons,
    ):
        """Test successful step analysis report generation."""
        mock_database.execution_repository.get_step_analysis = AsyncMock(
            return_value=sample_step_analysis
        )
        mock_database.execution_repository.get_step_durations = AsyncMock(
            return_value=sample_step_analysis[0]["durations"]
        )
        mock_database.execution_repository.get_failure_reasons_by_step = AsyncMock(
            return_value=sample_failure_reasons
        )

        generator = StepAnalysisReportGenerator(mock_database)
        report = await generator.generate()

        assert isinstance(report, StepAnalysisReport)
        assert report.total_steps == 2
        assert len(report.steps) == 2

    @pytest.mark.asyncio
    async def test_generate_identifies_most_failed_step(self, mock_database):
        """Test that most failed step is correctly identified."""
        mock_database.execution_repository.get_step_analysis = AsyncMock(
            return_value=[
                {"step_name": "Step A", "total_runs": 100, "fail_count": 5,
                 "avg_duration": 1000, "min_duration": 500, "max_duration": 2000,
                 "durations": [1000] * 10},
                {"step_name": "Step B", "total_runs": 100, "fail_count": 15,
                 "avg_duration": 2000, "min_duration": 1000, "max_duration": 4000,
                 "durations": [2000] * 10},
            ]
        )
        mock_database.execution_repository.get_step_durations = AsyncMock(
            return_value=[1000] * 10
        )
        mock_database.execution_repository.get_failure_reasons_by_step = AsyncMock(
            return_value=[]
        )

        generator = StepAnalysisReportGenerator(mock_database)
        report = await generator.generate()

        assert report.most_failed_step == "Step B"

    @pytest.mark.asyncio
    async def test_generate_identifies_slowest_step(self, mock_database):
        """Test that slowest step is correctly identified."""
        mock_database.execution_repository.get_step_analysis = AsyncMock(
            return_value=[
                {"step_name": "Fast Step", "total_runs": 100, "fail_count": 0,
                 "avg_duration": 500, "min_duration": 200, "max_duration": 800,
                 "durations": [500] * 10},
                {"step_name": "Slow Step", "total_runs": 100, "fail_count": 0,
                 "avg_duration": 5000, "min_duration": 3000, "max_duration": 8000,
                 "durations": [5000] * 10},
            ]
        )
        mock_database.execution_repository.get_step_durations = AsyncMock(
            side_effect=lambda step: [500] * 10 if step == "Fast Step" else [5000] * 10
        )
        mock_database.execution_repository.get_failure_reasons_by_step = AsyncMock(
            return_value=[]
        )

        generator = StepAnalysisReportGenerator(mock_database)
        report = await generator.generate()

        assert report.slowest_step == "Slow Step"

    @pytest.mark.asyncio
    async def test_generate_calculates_percentiles(self, mock_database):
        """Test that P50 and P95 are calculated correctly."""
        durations = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

        mock_database.execution_repository.get_step_analysis = AsyncMock(
            return_value=[
                {"step_name": "Test Step", "total_runs": 10, "fail_count": 0,
                 "avg_duration": 550, "min_duration": 100, "max_duration": 1000,
                 "durations": durations},
            ]
        )
        mock_database.execution_repository.get_step_durations = AsyncMock(
            return_value=durations
        )
        mock_database.execution_repository.get_failure_reasons_by_step = AsyncMock(
            return_value=[]
        )

        generator = StepAnalysisReportGenerator(mock_database)
        report = await generator.generate()

        step = report.steps[0]
        # P50 should be around 500-600
        assert 400 <= step.p50_duration <= 600
        # P95 should be around 900-1000
        assert 800 <= step.p95_duration <= 1000

    @pytest.mark.asyncio
    async def test_generate_includes_failure_reasons(
        self,
        mock_database,
        sample_failure_reasons,
    ):
        """Test that failure reasons are included in report."""
        mock_database.execution_repository.get_step_analysis = AsyncMock(
            return_value=[
                {"step_name": "Failing Step", "total_runs": 100, "fail_count": 10,
                 "avg_duration": 1000, "min_duration": 500, "max_duration": 2000,
                 "durations": [1000] * 10},
            ]
        )
        mock_database.execution_repository.get_step_durations = AsyncMock(
            return_value=[1000] * 10
        )
        mock_database.execution_repository.get_failure_reasons_by_step = AsyncMock(
            return_value=sample_failure_reasons
        )

        generator = StepAnalysisReportGenerator(mock_database)
        report = await generator.generate()

        step = report.steps[0]
        assert len(step.failure_reasons) == 3
        assert step.failure_reasons[0].error_message == "Timeout exceeded"
        assert step.failure_reasons[0].occurrence_count == 5
