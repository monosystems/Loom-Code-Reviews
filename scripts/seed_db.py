import asyncio
from uuid import uuid4

from src.database.connection import async_session_maker
from src.repositories.repository import RepositoryDAO
from src.repositories.job import JobDAO
from src.repositories.review import ReviewDAO
from src.repositories.finding import FindingDAO, Severity


async def seed_database():
    async with async_session_maker() as session:
        repo_dao = RepositoryDAO(session)
        job_dao = JobDAO(session)
        review_dao = ReviewDAO(session)
        finding_dao = FindingDAO(session)

        repo = await repo_dao.create(
            platform="github",
            platform_id="12345",
            full_name="test/repo",
            webhook_secret="secret123",
            is_active=True,
            config_cache={"auto_merge": True}
        )
        print(f"Created repository: {repo.id}")

        job = await job_dao.create_job(
            repo_id=repo.id,
            platform_pr_id="pr-001",
            pr_number=42,
            head_sha="abc123def456",
            priority=5
        )
        print(f"Created job: {job.id}")

        review = await review_dao.create_review(
            job_id=job.id,
            pr_number=42,
            pr_title="Add new feature",
            pr_author="developer",
            summary="Reviewed code changes",
            total_findings=3,
            blocker_count=1,
            warning_count=1,
            info_count=1
        )
        print(f"Created review: {review.id}")

        findings = await finding_dao.create_findings(
            review_id=review.id,
            findings_list=[
                {
                    "pipeline_name": "security",
                    "file_path": "src/auth.py",
                    "line_number": 45,
                    "severity": Severity.BLOCKER,
                    "category": "security",
                    "message": "SQL injection vulnerability detected",
                    "suggestion": "Use parameterized queries"
                },
                {
                    "pipeline_name": "style",
                    "file_path": "src/auth.py",
                    "line_number": 50,
                    "severity": Severity.WARNING,
                    "category": "style",
                    "message": "Line too long (120 chars)",
                    "suggestion": "Split line"
                },
                {
                    "pipeline_name": "docs",
                    "file_path": "README.md",
                    "line_number": 1,
                    "severity": Severity.INFO,
                    "category": "documentation",
                    "message": "Missing section in README",
                    "suggestion": "Add installation instructions"
                }
            ]
        )
        print(f"Created {len(findings)} findings")

        await session.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
