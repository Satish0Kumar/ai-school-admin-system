"""
Train ML Model Script
ScholarSense - AI-Powered Academic Intelligence System

Standalone script to train the ML model from scratch.
Can be run manually or scheduled for automated retraining.

Usage:
    python scripts/train_model.py [--force] [--verbose]

Options:
    --force: Force retraining even if model files exist
    --verbose: Show detailed training progress
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np
import pickle
from datetime import date, timedelta
from sqlalchemy import func

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix
)

# Project imports
from backend.database.db_config import SessionLocal
from backend.database.models import (
    Student, AcademicRecord, Attendance, BehavioralIncident
)

# ── Configuration ────────────────────────────────────────────────────────────
FEATURE_NAMES = [
    'age', 'grade', 'gender', 'socioeconomic_status', 'parent_education',
    'current_gpa', 'previous_gpa', 'grade_trend', 'attendance_rate',
    'failed_subjects', 'assignment_submission_rate', 'behavioral_incidents',
    'math_score', 'science_score', 'english_score', 'social_score',
    'language_score'
]

RISK_LABELS = {0: 'Low', 1: 'Medium', 2: 'High', 3: 'Critical'}

# Model save paths
MODEL_DIR = project_root / "models" / "saved_models"
MODEL_PATH = MODEL_DIR / "best_model.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
ENCODER_PATH = MODEL_DIR / "label_encoders.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.pkl"


# ==============================================================================
# STEP 1 — EXTRACT FEATURES FROM DATABASE
# ==============================================================================

def extract_features_from_db(verbose=False):
    """
    Extract all student features from PostgreSQL for ML training.
    Returns: (X, y) numpy arrays
    """
    if verbose:
        print("\n📦 Extracting features from database...")

    db = SessionLocal()
    features_list = []
    labels_list = []
    skipped = 0

    try:
        # Get all active students
        students = db.query(Student).filter(
            Student.is_active == True
        ).all()

        if verbose:
            print(f"   Found {len(students)} active students")

        for student in students:
            # ── Get latest academic record ──────────────────────────────────
            academic = db.query(AcademicRecord).filter(
                AcademicRecord.student_id == student.id
            ).order_by(AcademicRecord.recorded_date.desc()).first()

            if not academic:
                skipped += 1
                continue

            # ── Get attendance rate (last 90 days) ──────────────────────────
            ninety_days_ago = date.today() - timedelta(days=90)

            total_days = db.query(func.count(Attendance.id)).filter(
                Attendance.student_id == student.id,
                Attendance.attendance_date >= ninety_days_ago
            ).scalar() or 0

            present_days = db.query(func.count(Attendance.id)).filter(
                Attendance.student_id == student.id,
                Attendance.attendance_date >= ninety_days_ago,
                Attendance.status == 'present'
            ).scalar() or 0

            attendance_rate = (
                round(present_days / total_days * 100, 2)
                if total_days > 0 else 95.0
            )

            # ── Behavioral incidents (last 90 days) ─────────────────────────
            try:
                incident_count = db.query(
                    func.count(BehavioralIncident.id)
                ).filter(
                    BehavioralIncident.student_id == student.id,
                ).scalar() or 0
            except Exception:
                incident_count = 0

            # ── Encode categorical features ─────────────────────────────────
            gender_enc = 1 if student.gender == 'Male' else 0

            ses_map = {'Low': 0, 'Medium': 1, 'High': 2}
            ses_enc = ses_map.get(
                student.socioeconomic_status or 'Medium', 1
            )

            edu_map = {
                'None': 0, 'High School': 1,
                'Graduate': 2, 'Post-Graduate': 3
            }
            edu_enc = edu_map.get(
                student.parent_education or 'High School', 1
            )

            # ── Build feature vector ────────────────────────────────────────
            feature_vector = [
                student.computed_age,  # Use computed age from DOB
                student.grade,
                gender_enc,
                ses_enc,
                edu_enc,
                float(academic.current_gpa or 0),
                float(academic.previous_gpa or 0),
                float(academic.grade_trend or 0),
                attendance_rate,
                int(academic.failed_subjects or 0),
                float(academic.assignment_submission_rate or 80),
                incident_count,
                float(academic.math_score or 0),
                float(academic.science_score or 0),
                float(academic.english_score or 0),
                float(academic.social_score or 0),
                float(academic.language_score or 0),
            ]

            # ── Derive risk label from academic data ────────────────────────
            # Convert GPA (0-100) back to 0-20 scale for risk derivation
            g3_approx = int((float(academic.current_gpa or 0)) / 5)
            failures = int(academic.failed_subjects or 0)
            absences = total_days - present_days

            # Import risk derivation function
            from backend.scripts.uci_column_mapping import derive_risk_label
            risk_level, _ = derive_risk_label(g3_approx, failures, absences)

            features_list.append(feature_vector)
            labels_list.append(risk_level)

        if verbose:
            print(f"   ✅ Features extracted: {len(features_list)} students")
            print(f"   ⚠️  Skipped (no academic record): {skipped} students")

            # ── Show class distribution ─────────────────────────────────────────
            from collections import Counter
            dist = Counter(labels_list)
            print("
   📊 Risk Label Distribution:"            for level in sorted(dist.keys()):
                label = RISK_LABELS[level]
                count = dist[level]
                pct = count / len(labels_list) * 100
                bar = '█' * int(pct // 3)
                print(f"      {label:<10}: {count:3} students ({pct:5.1f}%)  {bar}")

        return np.array(features_list), np.array(labels_list)

    finally:
        db.close()


# ==============================================================================
# STEP 2 — TRAIN THE MODEL
# ==============================================================================

def train_model(X, y, verbose=False):
    """
    Train Gradient Boosting Classifier on extracted features.
    Returns: trained model, scaler, accuracy score
    """
    if verbose:
        print("\n🤖 Training ML Model...")

    # ── Train/test split ────────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    if verbose:
        print(f"   Train size : {len(X_train)} samples")
        print(f"   Test size  : {len(X_test)} samples")

    # ── Feature scaling ─────────────────────────────────────────────────────
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # ── Train Gradient Boosting Classifier ──────────────────────────────────
    if verbose:
        print("\n   ⏳ Training Gradient Boosting Classifier...")

    model = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=4,
        min_samples_leaf=2,
        subsample=0.8,
        random_state=42
    )
    model.fit(X_train_scaled, y_train)

    # ── Evaluate ─────────────────────────────────────────────────────────────
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)

    if verbose:
        print(".2f"
        # ── Cross validation ─────────────────────────────────────────────────────
        print("\n   📊 Running 5-fold cross validation...")
        cv_scores = cross_val_score(
            model, scaler.transform(X), y,
            cv=5, scoring='accuracy'
        )
        print(f"   CV Scores  : {[f'{s*100:.1f}%' for s in cv_scores]}")
        print(".2f"        print(".2f"        print(".2f"
        # ── Classification report ────────────────────────────────────────────────
        print("\n   📋 Classification Report:")
        print("   " + "-" * 55)
        report = classification_report(
            y_test, y_pred,
            target_names=['Low', 'Medium', 'High', 'Critical'],
            digits=3
        )
        for line in report.split('\n'):
            print(f"   {line}")

        # ── Feature importance ───────────────────────────────────────────────────
        print("\n   🔍 Top 10 Important Features:")
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        for i in range(min(10, len(FEATURE_NAMES))):
            feat = FEATURE_NAMES[indices[i]]
            imp = importances[indices[i]]
            bar = '█' * int(imp * 100)
            print(f"      {i+1:2}. {feat:<30} {imp:.4f}  {bar}")

    return model, scaler, accuracy


# ==============================================================================
# STEP 3 — SAVE MODEL & METADATA
# ==============================================================================

def save_model(model, scaler, accuracy, verbose=False):
    """
    Save trained model, scaler, and metadata to disk.
    """
    if verbose:
        print(f"\n💾 Saving model to {MODEL_DIR}...")

    # Create directory if it doesn't exist
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # ── Save model ───────────────────────────────────────────────────────────
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    if verbose:
        print(f"   ✅ Model saved     → {MODEL_PATH.name}")

    # ── Save scaler ──────────────────────────────────────────────────────────
    with open(SCALER_PATH, 'wb') as f:
        pickle.dump(scaler, f)
    if verbose:
        print(f"   ✅ Scaler saved    → {SCALER_PATH.name}")

    # ── Save metadata ────────────────────────────────────────────────────────
    metadata = {
        'model_type': 'GradientBoostingClassifier',
        'feature_names': FEATURE_NAMES,
        'risk_labels': RISK_LABELS,
        'accuracy': accuracy,
        'trained_on': date.today().isoformat(),
        'n_features': len(FEATURE_NAMES),
        'n_classes': 4,
        'pass_mark': 35,
        'version': '3.0',
        'script_version': 'train_model.py'
    }
    with open(METADATA_PATH, 'wb') as f:
        pickle.dump(metadata, f)
    if verbose:
        print(f"   ✅ Metadata saved  → {METADATA_PATH.name}")

    # ── File sizes ────────────────────────────────────────────────────────────
    if verbose:
        model_size = MODEL_PATH.stat().st_size / 1024
        scaler_size = SCALER_PATH.stat().st_size / 1024
        print(".1f"        print(".1f"


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description='Train ML model for ScholarSense')
    parser.add_argument('--force', action='store_true',
                       help='Force retraining even if model files exist')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed training progress')
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("  🤖 SCHOLARSENSE — ML MODEL TRAINING")
    print("=" * 70)

    # Check if model already exists
    if MODEL_PATH.exists() and not args.force:
        print(f"❌ Model already exists at {MODEL_PATH}")
        print("   Use --force to retrain anyway")
        sys.exit(1)

    # ── Step 1: Extract features ─────────────────────────────────────────────
    X, y = extract_features_from_db(verbose=args.verbose)

    if len(X) < 50:
        print("\n❌ Not enough data to train! Need at least 50 students.")
        print("   Add more student data first.")
        sys.exit(1)

    # ── Step 2: Train model ──────────────────────────────────────────────────
    model, scaler, accuracy = train_model(X, y, verbose=args.verbose)

    # ── Step 3: Save model ───────────────────────────────────────────────────
    save_model(model, scaler, accuracy, verbose=args.verbose)

    # ── Final summary ────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  ✅ MODEL TRAINING COMPLETE — SUMMARY")
    print("=" * 70)
    print(".2f"    print(f"  📦 Model saved to   : models/saved_models/best_model.pkl")
    print(f"  📅 Trained on       : {date.today().isoformat()}")
    print(f"  🔢 Features used    : {len(FEATURE_NAMES)}")
    print(f"  📊 Training samples : {len(X)}")
    print("=" * 70)
    print("\n🎉 Model training completed successfully!")
    print("   The ML model is ready for risk predictions.\n")


if __name__ == "__main__":
    main()