"""
One-off repair: legacy rows where confidence was scaled twice (> 100%).

Run from project root (venv active):
    python backend/scripts/fix_risk_prediction_scales.py

Does NOT use "probability > 1" — valid percentages are often > 1 (e.g. 25%).
Only fixes values clearly out of percentage range (> 100).
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text  # noqa: E402

from backend.database.db_config import SessionLocal  # noqa: E402


def main():
    db = SessionLocal()
    try:
        r1 = db.execute(
            text(
                """
                UPDATE risk_predictions
                SET confidence_score = confidence_score / 100
                WHERE confidence_score > 100
                """
            )
        )
        r2 = db.execute(
            text(
                """
                UPDATE risk_predictions
                SET
                    probability_low = CASE WHEN probability_low > 100
                        THEN probability_low / 100 ELSE probability_low END,
                    probability_medium = CASE WHEN probability_medium > 100
                        THEN probability_medium / 100 ELSE probability_medium END,
                    probability_high = CASE WHEN probability_high > 100
                        THEN probability_high / 100 ELSE probability_high END,
                    probability_critical = CASE WHEN probability_critical > 100
                        THEN probability_critical / 100 ELSE probability_critical END
                WHERE probability_low > 100
                   OR probability_medium > 100
                   OR probability_high > 100
                   OR probability_critical > 100
                """
            )
        )
        db.commit()
        print(f"Rows updated (confidence_score > 100): {r1.rowcount}")
        print(f"Rows updated (any probability > 100): {r2.rowcount}")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
